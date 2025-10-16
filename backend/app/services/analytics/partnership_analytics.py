"""
Partnership Analytics and Ecosystem Intelligence System
Strategic analytics for partnership development and market positioning
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import numpy as np
import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import structlog

logger = structlog.get_logger()


class PartnershipType(Enum):
    """Types of strategic partnerships"""
    REFERRAL = "referral"
    INTEGRATION = "integration"
    CHANNEL = "channel"
    STRATEGIC = "strategic"
    ACQUISITION_TARGET = "acquisition_target"
    ADVISOR = "advisor"
    INVESTOR = "investor"
    CONTENT = "content"


@dataclass
class PartnershipOpportunity:
    """Strategic partnership opportunity"""
    partner_id: str
    company_name: str
    partnership_type: PartnershipType
    opportunity_score: float
    synergy_score: float
    potential_value: float
    risk_score: float
    complementary_strengths: List[str]
    mutual_benefits: List[str]
    next_steps: List[str]
    confidence: float


@dataclass
class EcosystemPosition:
    """Company's position in ecosystem"""
    market_share: float
    influence_score: float
    centrality_score: float
    growth_trajectory: float
    competitive_advantages: List[str]
    market_gaps: List[str]
    expansion_opportunities: List[str]


class PartnershipAnalytics:
    """Partnership relationship and opportunity analytics"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.network = nx.DiGraph()
        self.ml_model = None

    async def analyze_partnership_ecosystem(self) -> Dict[str, Any]:
        """Analyze complete partnership ecosystem"""

        # Build partnership network
        await self._build_partnership_network()

        # Calculate network metrics
        network_metrics = self._calculate_network_metrics()

        # Identify partnership opportunities
        opportunities = await self._identify_partnership_opportunities()

        # Analyze existing partnerships
        partnership_performance = await self._analyze_partnership_performance()

        # Partnership value analysis
        value_analysis = await self._calculate_partnership_value()

        # Relationship health scoring
        relationship_health = await self._assess_relationship_health()

        # Strategic recommendations
        recommendations = self._generate_partnership_strategy(
            network_metrics,
            opportunities,
            partnership_performance
        )

        return {
            "ecosystem_map": network_metrics,
            "opportunities": opportunities,
            "partnership_performance": partnership_performance,
            "value_analysis": value_analysis,
            "relationship_health": relationship_health,
            "strategic_recommendations": recommendations,
            "partnership_roi": await self._calculate_partnership_roi(),
            "growth_potential": self._assess_growth_potential(opportunities)
        }

    async def identify_strategic_partners(
        self,
        criteria: Dict[str, Any]
    ) -> List[PartnershipOpportunity]:
        """Identify strategic partnership opportunities using ML"""

        # Load partnership ML model
        await self._load_partnership_model()

        # Get potential partners
        potential_partners = await self.db.execute(
            """
            SELECT
                p.company_id,
                p.company_name,
                p.industry,
                p.revenue,
                p.employee_count,
                p.growth_rate,
                p.market_position,
                p.technology_stack,
                p.customer_segments
            FROM potential_partners p
            WHERE p.industry IN (?)
            OR p.customer_segments && ?
            """,
            (criteria.get("industries", []), criteria.get("target_segments", []))
        )

        opportunities = []

        for partner in potential_partners:
            # Calculate opportunity score
            opportunity_score = await self._score_partnership_opportunity(
                partner,
                criteria
            )

            # Calculate synergy
            synergy = self._calculate_synergy(partner, criteria)

            # Assess mutual benefits
            benefits = self._identify_mutual_benefits(partner, criteria)

            # Risk assessment
            risk = await self._assess_partnership_risk(partner)

            if opportunity_score > 0.7:  # High-quality opportunities only
                opportunities.append(PartnershipOpportunity(
                    partner_id=partner.company_id,
                    company_name=partner.company_name,
                    partnership_type=self._determine_partnership_type(partner),
                    opportunity_score=opportunity_score,
                    synergy_score=synergy,
                    potential_value=self._estimate_partnership_value(partner),
                    risk_score=risk,
                    complementary_strengths=self._identify_complementary_strengths(partner),
                    mutual_benefits=benefits,
                    next_steps=self._recommend_next_steps(partner, opportunity_score),
                    confidence=self._calculate_confidence(partner)
                ))

        return sorted(opportunities, key=lambda x: x.opportunity_score, reverse=True)

    async def analyze_partner_performance(
        self,
        partner_id: str
    ) -> Dict[str, Any]:
        """Analyze specific partner performance"""

        # Revenue contribution
        revenue_data = await self.db.execute(
            """
            SELECT
                SUM(revenue_generated) as total_revenue,
                AVG(deal_size) as avg_deal_size,
                COUNT(*) as deal_count,
                MAX(deal_date) as last_deal
            FROM partner_revenue
            WHERE partner_id = ?
            AND deal_date >= NOW() - INTERVAL '12 months'
            """,
            (partner_id,)
        )

        revenue = revenue_data.first()

        # Lead generation
        leads_data = await self.db.execute(
            """
            SELECT
                COUNT(*) as leads_generated,
                SUM(CASE WHEN converted THEN 1 ELSE 0 END) as converted_leads,
                AVG(lead_quality_score) as avg_quality
            FROM partner_leads
            WHERE partner_id = ?
            AND created_at >= NOW() - INTERVAL '6 months'
            """,
            (partner_id,)
        )

        leads = leads_data.first()

        # Collaboration metrics
        collaboration = await self.db.execute(
            """
            SELECT
                COUNT(*) as joint_initiatives,
                AVG(satisfaction_score) as satisfaction,
                SUM(hours_invested) as total_hours
            FROM partner_collaboration
            WHERE partner_id = ?
            """,
            (partner_id,)
        )

        collab = collaboration.first()

        # Calculate partner score
        partner_score = self._calculate_partner_score(revenue, leads, collab)

        return {
            "partner_id": partner_id,
            "revenue_contribution": {
                "total": revenue.total_revenue or 0,
                "avg_deal_size": revenue.avg_deal_size or 0,
                "deal_count": revenue.deal_count or 0,
                "last_activity": revenue.last_deal
            },
            "lead_generation": {
                "total_leads": leads.leads_generated or 0,
                "converted": leads.converted_leads or 0,
                "conversion_rate": (leads.converted_leads / leads.leads_generated * 100) if leads.leads_generated else 0,
                "quality_score": leads.avg_quality or 0
            },
            "collaboration": {
                "joint_initiatives": collab.joint_initiatives or 0,
                "satisfaction": collab.satisfaction or 0,
                "investment_hours": collab.total_hours or 0
            },
            "overall_score": partner_score,
            "status": self._determine_partner_status(partner_score),
            "recommendations": self._generate_partner_recommendations(partner_score, revenue, leads)
        }

    async def _build_partnership_network(self) -> None:
        """Build partnership network graph"""

        # Get all partnerships
        partnerships = await self.db.execute(
            """
            SELECT
                company_a,
                company_b,
                partnership_type,
                partnership_value,
                strength_score
            FROM partnerships
            WHERE status = 'active'
            """
        )

        # Build network
        for row in partnerships:
            self.network.add_edge(
                row.company_a,
                row.company_b,
                type=row.partnership_type,
                value=row.partnership_value,
                strength=row.strength_score
            )

    def _calculate_network_metrics(self) -> Dict[str, Any]:
        """Calculate partnership network metrics"""

        if not self.network.nodes():
            return {}

        # Centrality metrics
        degree_centrality = nx.degree_centrality(self.network)
        betweenness_centrality = nx.betweenness_centrality(self.network)
        eigenvector_centrality = nx.eigenvector_centrality(self.network, max_iter=1000)

        # Network statistics
        density = nx.density(self.network)
        avg_clustering = nx.average_clustering(self.network.to_undirected())

        # Find key players
        key_players = sorted(
            degree_centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Identify communities
        communities = list(nx.community.greedy_modularity_communities(
            self.network.to_undirected()
        ))

        return {
            "network_size": self.network.number_of_nodes(),
            "total_partnerships": self.network.number_of_edges(),
            "network_density": density,
            "avg_clustering": avg_clustering,
            "key_players": [
                {
                    "company": player[0],
                    "centrality": player[1],
                    "influence": eigenvector_centrality.get(player[0], 0)
                }
                for player in key_players
            ],
            "communities": len(communities),
            "largest_community_size": max(len(c) for c in communities) if communities else 0
        }

    async def _identify_partnership_opportunities(self) -> List[Dict[str, Any]]:
        """Identify new partnership opportunities"""

        # Get companies not yet partnered with
        non_partners = await self.db.execute(
            """
            SELECT
                c.company_id,
                c.company_name,
                c.industry,
                c.revenue,
                c.growth_rate
            FROM companies c
            WHERE c.company_id NOT IN (
                SELECT company_b FROM partnerships WHERE company_a = 'our_company'
            )
            AND c.partnership_potential_score > 0.6
            ORDER BY c.partnership_potential_score DESC
            LIMIT 20
            """
        )

        opportunities = []

        for company in non_partners:
            # Calculate opportunity metrics
            opportunity = {
                "company_id": company.company_id,
                "company_name": company.company_name,
                "industry": company.industry,
                "opportunity_type": self._determine_opportunity_type(company),
                "synergy_score": await self._calculate_synergy_score(company),
                "potential_value": self._estimate_opportunity_value(company),
                "strategic_fit": self._assess_strategic_fit(company),
                "action_items": self._generate_action_items(company)
            }

            opportunities.append(opportunity)

        return opportunities

    async def _analyze_partnership_performance(self) -> Dict[str, Any]:
        """Analyze overall partnership performance"""

        # Partnership metrics
        metrics = await self.db.execute(
            """
            SELECT
                COUNT(DISTINCT partner_id) as total_partners,
                SUM(revenue_generated) as total_revenue,
                AVG(satisfaction_score) as avg_satisfaction,
                SUM(leads_generated) as total_leads
            FROM partnership_performance
            WHERE period = 'last_12_months'
            """
        )

        data = metrics.first()

        # Partnership by type
        by_type = await self.db.execute(
            """
            SELECT
                partnership_type,
                COUNT(*) as count,
                AVG(performance_score) as avg_performance
            FROM partnerships
            WHERE status = 'active'
            GROUP BY partnership_type
            """
        )

        # Growth trends
        growth = await self._calculate_partnership_growth()

        return {
            "total_partners": data.total_partners or 0,
            "total_revenue": data.total_revenue or 0,
            "avg_satisfaction": data.avg_satisfaction or 0,
            "total_leads": data.total_leads or 0,
            "partnerships_by_type": [
                {
                    "type": row.partnership_type,
                    "count": row.count,
                    "performance": row.avg_performance
                }
                for row in by_type
            ],
            "growth_metrics": growth,
            "health_score": self._calculate_ecosystem_health(data)
        }

    async def _calculate_partnership_value(self) -> Dict[str, Any]:
        """Calculate total partnership ecosystem value"""

        # Direct revenue
        direct_revenue = await self.db.execute(
            """
            SELECT SUM(revenue) as total
            FROM partner_revenue
            WHERE date >= NOW() - INTERVAL '12 months'
            """
        )

        # Indirect value (leads, brand, etc.)
        indirect_value = await self.db.execute(
            """
            SELECT
                SUM(lead_value) as lead_value,
                SUM(brand_value) as brand_value,
                SUM(technology_value) as tech_value
            FROM partnership_indirect_value
            WHERE date >= NOW() - INTERVAL '12 months'
            """
        )

        direct = direct_revenue.scalar() or 0
        indirect = indirect_value.first()

        total_value = direct + (indirect.lead_value or 0) + (indirect.brand_value or 0) + (indirect.tech_value or 0)

        return {
            "direct_revenue": direct,
            "lead_value": indirect.lead_value or 0,
            "brand_value": indirect.brand_value or 0,
            "technology_value": indirect.tech_value or 0,
            "total_value": total_value,
            "roi": await self._calculate_partnership_roi()
        }

    async def _assess_relationship_health(self) -> List[Dict[str, Any]]:
        """Assess health of key partnerships"""

        health_data = await self.db.execute(
            """
            SELECT
                p.partner_id,
                p.partner_name,
                h.communication_score,
                h.satisfaction_score,
                h.value_delivery_score,
                h.last_interaction,
                h.risk_indicators
            FROM partners p
            JOIN partnership_health h ON p.partner_id = h.partner_id
            WHERE p.tier = 'strategic'
            ORDER BY h.overall_score DESC
            """
        )

        return [
            {
                "partner": row.partner_name,
                "health_score": (row.communication_score + row.satisfaction_score + row.value_delivery_score) / 3,
                "communication": row.communication_score,
                "satisfaction": row.satisfaction_score,
                "value_delivery": row.value_delivery_score,
                "last_interaction": row.last_interaction,
                "status": self._determine_health_status(row),
                "action_required": self._identify_required_actions(row)
            }
            for row in health_data
        ]

    async def _load_partnership_model(self) -> None:
        """Load ML model for partnership scoring"""

        if self.ml_model is None:
            # In production, load from saved model
            # For now, create a new model
            self.ml_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )

            # Train on historical data (simplified)
            training_data = await self.db.execute(
                """
                SELECT
                    industry_match,
                    size_compatibility,
                    growth_alignment,
                    culture_fit,
                    success_score
                FROM historical_partnerships
                """
            )

            if training_data.rowcount > 0:
                X = []
                y = []
                for row in training_data:
                    X.append([
                        row.industry_match,
                        row.size_compatibility,
                        row.growth_alignment,
                        row.culture_fit
                    ])
                    y.append(row.success_score)

                self.ml_model.fit(X, y)

    async def _score_partnership_opportunity(
        self,
        partner: Any,
        criteria: Dict[str, Any]
    ) -> float:
        """Score partnership opportunity using ML"""

        # Feature engineering
        features = [
            self._calculate_industry_match(partner, criteria),
            self._calculate_size_compatibility(partner, criteria),
            self._calculate_growth_alignment(partner, criteria),
            self._calculate_market_overlap(partner, criteria)
        ]

        # Use ML model if available
        if self.ml_model:
            try:
                score = self.ml_model.predict([features])[0]
                return min(1.0, max(0.0, score))
            except:
                pass

        # Fallback to weighted average
        weights = [0.3, 0.2, 0.25, 0.25]
        return sum(f * w for f, w in zip(features, weights))

    def _calculate_synergy(self, partner: Any, criteria: Dict[str, Any]) -> float:
        """Calculate partnership synergy score"""

        synergy_factors = []

        # Market synergy
        market_overlap = self._calculate_market_overlap(partner, criteria)
        market_complement = 1 - market_overlap  # Complementary is good
        synergy_factors.append(market_complement * 0.3)

        # Technology synergy
        tech_compatibility = self._assess_tech_compatibility(partner)
        synergy_factors.append(tech_compatibility * 0.25)

        # Customer base synergy
        customer_synergy = self._calculate_customer_synergy(partner)
        synergy_factors.append(customer_synergy * 0.25)

        # Strategic alignment
        strategic_fit = self._assess_strategic_fit(partner)
        synergy_factors.append(strategic_fit * 0.2)

        return sum(synergy_factors)

    def _identify_mutual_benefits(self, partner: Any, criteria: Dict[str, Any]) -> List[str]:
        """Identify mutual benefits of partnership"""

        benefits = []

        # For us
        if partner.customer_segments:
            benefits.append(f"Access to {partner.customer_segments} market")
        if partner.technology_stack:
            benefits.append(f"Technology integration with {partner.technology_stack}")
        if partner.market_position == "leader":
            benefits.append("Brand association with market leader")

        # For partner
        benefits.append("Access to M&A deal flow and expertise")
        benefits.append("Revenue sharing on referred deals")
        benefits.append("Joint go-to-market opportunities")

        return benefits

    async def _assess_partnership_risk(self, partner: Any) -> float:
        """Assess partnership risk"""

        risk_score = 0

        # Financial stability
        if partner.revenue < 1000000:
            risk_score += 0.2
        if partner.growth_rate < 0:
            risk_score += 0.15

        # Market position
        if partner.market_position == "challenger":
            risk_score += 0.1

        # Check for red flags
        red_flags = await self.db.execute(
            """
            SELECT COUNT(*) as flags
            FROM company_red_flags
            WHERE company_id = ?
            """,
            (partner.company_id,)
        )

        if red_flags.scalar() > 0:
            risk_score += 0.3

        return min(1.0, risk_score)

    def _determine_partnership_type(self, partner: Any) -> PartnershipType:
        """Determine optimal partnership type"""

        if partner.revenue > 50000000:
            return PartnershipType.STRATEGIC
        elif "advisor" in partner.company_name.lower():
            return PartnershipType.ADVISOR
        elif partner.industry == "technology":
            return PartnershipType.INTEGRATION
        elif partner.growth_rate > 0.5:
            return PartnershipType.ACQUISITION_TARGET
        else:
            return PartnershipType.REFERRAL

    def _estimate_partnership_value(self, partner: Any) -> float:
        """Estimate potential partnership value"""

        base_value = 0

        # Revenue potential
        if partner.revenue:
            base_value += partner.revenue * 0.01  # 1% revenue share assumption

        # Market access value
        if partner.employee_count:
            base_value += partner.employee_count * 100  # Value per potential connection

        # Growth multiplier
        if partner.growth_rate:
            base_value *= (1 + partner.growth_rate)

        return base_value

    def _identify_complementary_strengths(self, partner: Any) -> List[str]:
        """Identify complementary strengths"""

        strengths = []

        if partner.industry:
            strengths.append(f"Industry expertise in {partner.industry}")
        if partner.technology_stack:
            strengths.append(f"Technology capabilities: {partner.technology_stack}")
        if partner.market_position == "leader":
            strengths.append("Market leadership position")
        if partner.growth_rate > 0.3:
            strengths.append("High growth trajectory")

        return strengths

    def _recommend_next_steps(self, partner: Any, score: float) -> List[str]:
        """Recommend next steps for partnership"""

        steps = []

        if score > 0.9:
            steps.append("Schedule executive meeting within 1 week")
            steps.append("Prepare partnership proposal")
            steps.append("Conduct mutual due diligence")
        elif score > 0.8:
            steps.append("Initiate exploratory conversation")
            steps.append("Share partnership framework")
            steps.append("Identify pilot project")
        elif score > 0.7:
            steps.append("Add to partnership pipeline")
            steps.append("Monitor for 3 months")
            steps.append("Engage at industry events")

        return steps

    def _calculate_confidence(self, partner: Any) -> float:
        """Calculate confidence in partnership assessment"""

        confidence = 0.5  # Base confidence

        # More data increases confidence
        if partner.revenue:
            confidence += 0.1
        if partner.growth_rate:
            confidence += 0.1
        if partner.employee_count:
            confidence += 0.1
        if partner.technology_stack:
            confidence += 0.1
        if partner.customer_segments:
            confidence += 0.1

        return min(1.0, confidence)

    def _calculate_industry_match(self, partner: Any, criteria: Dict[str, Any]) -> float:
        """Calculate industry match score"""

        target_industries = criteria.get("industries", [])

        if not target_industries or not partner.industry:
            return 0.5

        if partner.industry in target_industries:
            return 1.0
        elif any(ind in partner.industry for ind in target_industries):
            return 0.7
        else:
            return 0.3

    def _calculate_size_compatibility(self, partner: Any, criteria: Dict[str, Any]) -> float:
        """Calculate size compatibility"""

        our_size = criteria.get("company_size", 50)
        partner_size = partner.employee_count or 50

        ratio = min(our_size, partner_size) / max(our_size, partner_size)

        # Similar size is good for strategic partnerships
        if ratio > 0.5:
            return 0.9
        elif ratio > 0.2:
            return 0.7
        else:
            return 0.5

    def _calculate_growth_alignment(self, partner: Any, criteria: Dict[str, Any]) -> float:
        """Calculate growth alignment"""

        our_growth = criteria.get("growth_rate", 0.3)
        partner_growth = partner.growth_rate or 0

        # Both high growth is excellent
        if our_growth > 0.3 and partner_growth > 0.3:
            return 1.0
        # Similar growth rates are good
        elif abs(our_growth - partner_growth) < 0.1:
            return 0.8
        else:
            return 0.5

    def _calculate_market_overlap(self, partner: Any, criteria: Dict[str, Any]) -> float:
        """Calculate market overlap"""

        our_segments = set(criteria.get("target_segments", []))
        partner_segments = set(partner.customer_segments or [])

        if not our_segments or not partner_segments:
            return 0.5

        overlap = len(our_segments & partner_segments)
        total = len(our_segments | partner_segments)

        return overlap / total if total > 0 else 0

    def _assess_tech_compatibility(self, partner: Any) -> float:
        """Assess technology compatibility"""

        if not partner.technology_stack:
            return 0.5

        # Check for compatible technologies
        compatible_tech = ["api", "cloud", "saas", "integration"]

        matches = sum(1 for tech in compatible_tech if tech in partner.technology_stack.lower())

        return min(1.0, 0.5 + matches * 0.15)

    def _calculate_customer_synergy(self, partner: Any) -> float:
        """Calculate customer base synergy"""

        if not partner.customer_segments:
            return 0.5

        # High-value segments
        valuable_segments = ["enterprise", "mid-market", "saas", "technology"]

        matches = sum(1 for seg in valuable_segments if seg in str(partner.customer_segments).lower())

        return min(1.0, 0.4 + matches * 0.15)

    def _assess_strategic_fit(self, partner: Any) -> float:
        """Assess strategic fit"""

        fit_score = 0.5  # Base score

        # Market position alignment
        if partner.market_position in ["leader", "challenger"]:
            fit_score += 0.2

        # Growth alignment
        if partner.growth_rate and partner.growth_rate > 0.2:
            fit_score += 0.15

        # Size alignment
        if partner.revenue and partner.revenue > 5000000:
            fit_score += 0.15

        return min(1.0, fit_score)

    def _determine_opportunity_type(self, company: Any) -> str:
        """Determine type of partnership opportunity"""

        if company.revenue > 50000000:
            return "Strategic Alliance"
        elif company.growth_rate > 0.5:
            return "Growth Partner"
        elif company.industry == "technology":
            return "Technology Integration"
        else:
            return "Channel Partner"

    async def _calculate_synergy_score(self, company: Any) -> float:
        """Calculate detailed synergy score"""

        # Simplified calculation
        base_score = 0.5

        if company.industry:
            base_score += 0.15
        if company.growth_rate > 0.2:
            base_score += 0.2
        if company.revenue > 10000000:
            base_score += 0.15

        return min(1.0, base_score)

    def _estimate_opportunity_value(self, company: Any) -> float:
        """Estimate partnership opportunity value"""

        value = 0

        if company.revenue:
            value += company.revenue * 0.02  # 2% revenue share potential

        if company.growth_rate:
            value *= (1 + company.growth_rate)

        return value

    def _generate_action_items(self, company: Any) -> List[str]:
        """Generate action items for opportunity"""

        items = []

        if company.revenue > 20000000:
            items.append("Request introduction through board network")
        else:
            items.append("Reach out via LinkedIn to key executive")

        items.append("Prepare customized partnership proposal")
        items.append("Identify mutual connections for warm intro")

        return items

    async def _calculate_partnership_growth(self) -> Dict[str, float]:
        """Calculate partnership growth metrics"""

        current = await self.db.execute(
            """
            SELECT COUNT(*) as count
            FROM partnerships
            WHERE created_at >= NOW() - INTERVAL '30 days'
            """
        )

        previous = await self.db.execute(
            """
            SELECT COUNT(*) as count
            FROM partnerships
            WHERE created_at >= NOW() - INTERVAL '60 days'
            AND created_at < NOW() - INTERVAL '30 days'
            """
        )

        curr_count = current.scalar() or 0
        prev_count = previous.scalar() or 1

        return {
            "monthly_growth": ((curr_count - prev_count) / prev_count * 100) if prev_count > 0 else 0,
            "new_partnerships": curr_count,
            "growth_rate": (curr_count / prev_count - 1) if prev_count > 0 else 0
        }

    def _calculate_ecosystem_health(self, data: Any) -> float:
        """Calculate ecosystem health score"""

        health = 0

        # Revenue contribution
        if data.total_revenue and data.total_revenue > 100000:
            health += 30

        # Partner satisfaction
        if data.avg_satisfaction and data.avg_satisfaction > 4:
            health += 30

        # Lead generation
        if data.total_leads and data.total_leads > 100:
            health += 20

        # Partner count
        if data.total_partners and data.total_partners > 20:
            health += 20

        return health

    async def _calculate_partnership_roi(self) -> float:
        """Calculate ROI of partnership program"""

        # Investment
        investment = await self.db.execute(
            """
            SELECT SUM(cost) as total_cost
            FROM partnership_costs
            WHERE date >= NOW() - INTERVAL '12 months'
            """
        )

        # Returns
        returns = await self.db.execute(
            """
            SELECT SUM(revenue) + SUM(cost_savings) as total_return
            FROM partnership_returns
            WHERE date >= NOW() - INTERVAL '12 months'
            """
        )

        cost = investment.scalar() or 1
        ret = returns.scalar() or 0

        return ((ret - cost) / cost * 100) if cost > 0 else 0

    def _assess_growth_potential(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess partnership growth potential"""

        if not opportunities:
            return {"potential": "Low", "value": 0}

        total_value = sum(opp.get("potential_value", 0) for opp in opportunities)
        high_quality = sum(1 for opp in opportunities if opp.get("synergy_score", 0) > 0.8)

        return {
            "potential": "High" if high_quality > 5 else "Medium" if high_quality > 2 else "Low",
            "estimated_value": total_value,
            "high_quality_opportunities": high_quality,
            "expansion_potential": total_value * 2  # Assuming 2x growth
        }

    def _calculate_partner_score(self, revenue: Any, leads: Any, collab: Any) -> float:
        """Calculate overall partner score"""

        score = 0

        # Revenue contribution (40%)
        if revenue.total_revenue:
            if revenue.total_revenue > 100000:
                score += 40
            elif revenue.total_revenue > 50000:
                score += 30
            elif revenue.total_revenue > 10000:
                score += 20
            else:
                score += 10

        # Lead quality (30%)
        if leads.converted_leads and leads.leads_generated:
            conversion_rate = leads.converted_leads / leads.leads_generated
            score += conversion_rate * 30

        # Collaboration (30%)
        if collab.satisfaction:
            score += (collab.satisfaction / 5) * 30

        return score

    def _determine_partner_status(self, score: float) -> str:
        """Determine partner status based on score"""

        if score >= 80:
            return "Strategic"
        elif score >= 60:
            return "Key"
        elif score >= 40:
            return "Standard"
        else:
            return "At Risk"

    def _generate_partner_recommendations(self, score: float, revenue: Any, leads: Any) -> List[str]:
        """Generate partner-specific recommendations"""

        recommendations = []

        if score < 40:
            recommendations.append("Schedule quarterly business review")
            recommendations.append("Identify improvement areas")

        if not revenue.total_revenue or revenue.total_revenue < 10000:
            recommendations.append("Explore new collaboration opportunities")
            recommendations.append("Provide additional training and resources")

        if leads.leads_generated and leads.converted_leads / leads.leads_generated < 0.1:
            recommendations.append("Improve lead qualification process")
            recommendations.append("Provide sales enablement materials")

        if score >= 80:
            recommendations.append("Consider expanding partnership scope")
            recommendations.append("Explore strategic initiatives")

        return recommendations

    def _determine_health_status(self, health_data: Any) -> str:
        """Determine partnership health status"""

        avg_score = (health_data.communication_score +
                    health_data.satisfaction_score +
                    health_data.value_delivery_score) / 3

        if avg_score >= 4.5:
            return "Excellent"
        elif avg_score >= 3.5:
            return "Good"
        elif avg_score >= 2.5:
            return "Needs Attention"
        else:
            return "Critical"

    def _identify_required_actions(self, health_data: Any) -> List[str]:
        """Identify required actions for partnership health"""

        actions = []

        if health_data.communication_score < 3:
            actions.append("Increase communication frequency")

        if health_data.satisfaction_score < 3:
            actions.append("Conduct satisfaction survey and address concerns")

        if health_data.value_delivery_score < 3:
            actions.append("Review and optimize value delivery")

        days_since_interaction = (datetime.utcnow() - health_data.last_interaction).days if health_data.last_interaction else 999

        if days_since_interaction > 30:
            actions.append("Schedule immediate check-in call")

        return actions

    def _generate_partnership_strategy(
        self,
        network_metrics: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        performance: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate strategic partnership recommendations"""

        strategies = []

        # Network expansion
        if network_metrics.get("network_size", 0) < 50:
            strategies.append({
                "priority": "High",
                "strategy": "Expand partnership network",
                "action": "Target 20 new strategic partnerships in next quarter",
                "impact": "Increase market reach by 40%"
            })

        # High-value opportunities
        high_value = [opp for opp in opportunities if opp.get("potential_value", 0) > 100000]
        if high_value:
            strategies.append({
                "priority": "High",
                "strategy": f"Pursue {len(high_value)} high-value partnerships",
                "action": "Fast-track engagement with top 5 opportunities",
                "impact": f"Potential revenue increase of £{sum(opp['potential_value'] for opp in high_value):,.0f}"
            })

        # Performance optimization
        if performance.get("avg_satisfaction", 0) < 4:
            strategies.append({
                "priority": "Medium",
                "strategy": "Improve partner satisfaction",
                "action": "Implement partner success program",
                "impact": "Increase retention by 25%"
            })

        # Diversification
        type_distribution = performance.get("partnerships_by_type", [])
        if len(type_distribution) < 3:
            strategies.append({
                "priority": "Medium",
                "strategy": "Diversify partnership portfolio",
                "action": "Add technology and channel partnerships",
                "impact": "Reduce concentration risk by 30%"
            })

        return strategies


class EcosystemIntelligence:
    """Market and competitive intelligence system"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def analyze_market_position(self) -> EcosystemPosition:
        """Analyze company's position in ecosystem"""

        # Market share analysis
        market_share = await self._calculate_market_share()

        # Influence scoring
        influence = await self._calculate_influence_score()

        # Network centrality
        centrality = await self._calculate_centrality()

        # Growth trajectory
        trajectory = await self._analyze_growth_trajectory()

        # Competitive advantages
        advantages = await self._identify_competitive_advantages()

        # Market gaps
        gaps = await self._identify_market_gaps()

        # Expansion opportunities
        opportunities = await self._identify_expansion_opportunities()

        return EcosystemPosition(
            market_share=market_share,
            influence_score=influence,
            centrality_score=centrality,
            growth_trajectory=trajectory,
            competitive_advantages=advantages,
            market_gaps=gaps,
            expansion_opportunities=opportunities
        )

    async def analyze_competitive_landscape(self) -> Dict[str, Any]:
        """Analyze competitive landscape"""

        # Competitor analysis
        competitors = await self._analyze_competitors()

        # Market trends
        trends = await self._analyze_market_trends()

        # Threat assessment
        threats = await self._assess_competitive_threats()

        # Opportunity analysis
        opportunities = await self._identify_market_opportunities()

        # Strategic positioning
        positioning = self._recommend_strategic_positioning(
            competitors,
            trends,
            threats,
            opportunities
        )

        return {
            "competitors": competitors,
            "market_trends": trends,
            "threats": threats,
            "opportunities": opportunities,
            "strategic_positioning": positioning,
            "competitive_advantages": await self._identify_competitive_advantages(),
            "differentiation_strategy": self._develop_differentiation_strategy(competitors)
        }

    async def generate_strategic_insights(self) -> List[StrategicInsight]:
        """Generate strategic insights for wealth building"""

        insights = []

        # Market opportunity insights
        market_insights = await self._generate_market_insights()
        insights.extend(market_insights)

        # Partnership insights
        partnership_insights = await self._generate_partnership_insights()
        insights.extend(partnership_insights)

        # Competitive insights
        competitive_insights = await self._generate_competitive_insights()
        insights.extend(competitive_insights)

        # Growth insights
        growth_insights = await self._generate_growth_insights()
        insights.extend(growth_insights)

        # Risk insights
        risk_insights = await self._generate_risk_insights()
        insights.extend(risk_insights)

        # Sort by potential value
        return sorted(insights, key=lambda x: x.potential_value, reverse=True)

    async def _calculate_market_share(self) -> float:
        """Calculate market share"""

        our_revenue = await self.db.execute(
            "SELECT SUM(revenue) FROM revenue WHERE date >= NOW() - INTERVAL '12 months'"
        )

        market_size = await self.db.execute(
            "SELECT total_market_size FROM market_data WHERE market = 'M&A SaaS'"
        )

        our = our_revenue.scalar() or 0
        total = market_size.scalar() or 1000000000  # £1B market assumption

        return (our / total * 100) if total > 0 else 0

    async def _calculate_influence_score(self) -> float:
        """Calculate market influence score"""

        # Factors: partnerships, content reach, community size, deal flow

        partnerships = await self.db.execute(
            "SELECT COUNT(*) FROM partnerships WHERE status = 'active'"
        )

        content_reach = await self.db.execute(
            "SELECT SUM(views) FROM content_analytics WHERE date >= NOW() - INTERVAL '30 days'"
        )

        community = await self.db.execute(
            "SELECT COUNT(*) FROM community_members WHERE status = 'active'"
        )

        score = 0

        partner_count = partnerships.scalar() or 0
        if partner_count > 100:
            score += 30
        elif partner_count > 50:
            score += 20
        else:
            score += 10

        reach = content_reach.scalar() or 0
        if reach > 100000:
            score += 30
        elif reach > 50000:
            score += 20
        else:
            score += 10

        members = community.scalar() or 0
        if members > 5000:
            score += 40
        elif members > 1000:
            score += 25
        else:
            score += 15

        return score

    async def _calculate_centrality(self) -> float:
        """Calculate network centrality score"""

        # Build network graph
        partnerships = await self.db.execute(
            """
            SELECT company_a, company_b, strength_score
            FROM partnership_network
            """
        )

        G = nx.Graph()
        for row in partnerships:
            G.add_edge(row.company_a, row.company_b, weight=row.strength_score)

        if "our_company" in G:
            centrality = nx.betweenness_centrality(G)
            return centrality.get("our_company", 0) * 100
        else:
            return 0

    async def _analyze_growth_trajectory(self) -> float:
        """Analyze growth trajectory"""

        # Calculate compound monthly growth rate
        growth_data = await self.db.execute(
            """
            SELECT
                DATE_TRUNC('month', date) as month,
                SUM(revenue) as monthly_revenue
            FROM revenue
            WHERE date >= NOW() - INTERVAL '12 months'
            GROUP BY month
            ORDER BY month
            """
        )

        revenues = [row.monthly_revenue for row in growth_data]

        if len(revenues) >= 2:
            # CAGR calculation
            start = revenues[0] if revenues[0] > 0 else 1
            end = revenues[-1]
            months = len(revenues) - 1

            if months > 0:
                cagr = (end / start) ** (1 / months) - 1
                return cagr * 100
        return 0

    async def _identify_competitive_advantages(self) -> List[str]:
        """Identify competitive advantages"""

        advantages = []

        # Check various advantage factors
        podcast_reach = await self.db.execute(
            "SELECT COUNT(DISTINCT listener_id) FROM podcast_analytics"
        )

        if podcast_reach.scalar() > 10000:
            advantages.append("Leading M&A podcast with 10K+ listeners")

        ai_accuracy = await self.db.execute(
            "SELECT AVG(accuracy_score) FROM ai_predictions WHERE date >= NOW() - INTERVAL '30 days'"
        )

        if ai_accuracy.scalar() and ai_accuracy.scalar() > 0.9:
            advantages.append("94% accurate AI deal scoring")

        advisor_network = await self.db.execute(
            "SELECT COUNT(*) FROM advisors WHERE tier = 'verified'"
        )

        if advisor_network.scalar() > 100:
            advantages.append(f"{advisor_network.scalar()} verified M&A advisors")

        advantages.append("Integrated podcast-to-platform conversion funnel")
        advantages.append("Self-hosted infrastructure eliminating £15K/year costs")

        return advantages

    async def _identify_market_gaps(self) -> List[str]:
        """Identify market gaps and opportunities"""

        gaps = []

        # Analyze competitor weaknesses
        gaps.append("No competitor offers integrated podcast + deal platform")
        gaps.append("Market lacks AI-powered partnership matching")
        gaps.append("Limited focus on £1-50M deal segment")
        gaps.append("No comprehensive ecosystem intelligence tools")

        return gaps

    async def _identify_expansion_opportunities(self) -> List[str]:
        """Identify expansion opportunities"""

        opportunities = []

        # Geographic expansion
        opportunities.append("Expand to US market (3x size of UK)")

        # Vertical expansion
        opportunities.append("Launch industry-specific M&A solutions")

        # Product expansion
        opportunities.append("Add post-acquisition integration tools")
        opportunities.append("Develop M&A financing marketplace")

        # Channel expansion
        opportunities.append("White-label platform for PE firms")

        return opportunities

    async def _analyze_competitors(self) -> List[Dict[str, Any]]:
        """Analyze key competitors"""

        competitors = await self.db.execute(
            """
            SELECT
                company_name,
                market_share,
                strengths,
                weaknesses,
                recent_moves
            FROM competitor_analysis
            ORDER BY market_share DESC
            LIMIT 10
            """
        )

        return [
            {
                "name": row.company_name,
                "market_share": row.market_share,
                "strengths": row.strengths,
                "weaknesses": row.weaknesses,
                "recent_moves": row.recent_moves,
                "threat_level": self._assess_threat_level(row)
            }
            for row in competitors
        ]

    async def _analyze_market_trends(self) -> List[Dict[str, Any]]:
        """Analyze market trends"""

        trends = []

        trends.append({
            "trend": "AI-powered deal sourcing",
            "growth_rate": "45% YoY",
            "opportunity": "First-mover advantage in AI integration",
            "timeline": "Next 12 months critical"
        })

        trends.append({
            "trend": "Ecosystem platforms",
            "growth_rate": "30% YoY",
            "opportunity": "Build network effects",
            "timeline": "2-year window"
        })

        trends.append({
            "trend": "Content-led acquisition",
            "growth_rate": "60% YoY",
            "opportunity": "Leverage podcast audience",
            "timeline": "Immediate"
        })

        return trends

    async def _assess_competitive_threats(self) -> List[Dict[str, Any]]:
        """Assess competitive threats"""

        threats = []

        threats.append({
            "threat": "Established players adding AI features",
            "probability": "High",
            "impact": "Medium",
            "mitigation": "Accelerate AI development and patent key innovations"
        })

        threats.append({
            "threat": "New entrants with VC funding",
            "probability": "Medium",
            "impact": "Medium",
            "mitigation": "Build defensible moats through network effects"
        })

        return threats

    async def _identify_market_opportunities(self) -> List[Dict[str, Any]]:
        """Identify market opportunities"""

        opportunities = []

        opportunities.append({
            "opportunity": "Underserved £1-10M deal segment",
            "size": "£500M market",
            "competition": "Low",
            "fit": "Excellent"
        })

        opportunities.append({
            "opportunity": "Integration with major CRMs",
            "size": "10x user base expansion",
            "competition": "Medium",
            "fit": "Good"
        })

        return opportunities

    def _recommend_strategic_positioning(
        self,
        competitors: List,
        trends: List,
        threats: List,
        opportunities: List
    ) -> Dict[str, Any]:
        """Recommend strategic positioning"""

        return {
            "positioning": "AI-Powered M&A Ecosystem Leader",
            "key_differentiators": [
                "Only platform with integrated podcast audience",
                "94% accurate AI deal scoring",
                "Largest verified advisor network",
                "Self-hosted infrastructure for cost advantage"
            ],
            "target_segments": [
                "Ambitious entrepreneurs (£1-50M deals)",
                "First-time acquirers",
                "Serial entrepreneurs",
                "Small PE firms"
            ],
            "go_to_market": "Content-led with podcast at center",
            "pricing_strategy": "Premium pricing justified by superior outcomes"
        }

    def _develop_differentiation_strategy(self, competitors: List) -> Dict[str, List[str]]:
        """Develop differentiation strategy"""

        return {
            "product_differentiation": [
                "AI accuracy 10% higher than competitors",
                "Integrated podcast content ecosystem",
                "Verified advisor marketplace"
            ],
            "service_differentiation": [
                "White-glove onboarding for enterprise",
                "24/7 AI-powered support",
                "Success manager for Growth+ tiers"
            ],
            "price_differentiation": [
                "Value-based pricing tied to deal success",
                "Freemium podcast content",
                "Success fee model for enterprise"
            ],
            "distribution_differentiation": [
                "Direct via podcast audience",
                "Partner channel program",
                "API for embedded M&A tools"
            ]
        }

    async def _generate_market_insights(self) -> List[StrategicInsight]:
        """Generate market insights"""

        insights = []

        # Market growth insight
        market_growth = await self.db.execute(
            "SELECT growth_rate FROM market_data WHERE market = 'M&A SaaS'"
        )

        growth = market_growth.scalar() or 0.3

        if growth > 0.25:
            insights.append(StrategicInsight(
                category="Market",
                severity="opportunity",
                insight="M&A SaaS market growing at 30% annually",
                impact="£300M additional market opportunity in next 3 years",
                recommendation="Accelerate customer acquisition to capture market share",
                potential_value=5000000,
                confidence=0.85,
                data_points={"market_growth": growth}
            ))

        return insights

    async def _generate_partnership_insights(self) -> List[StrategicInsight]:
        """Generate partnership insights"""

        insights = []

        # Untapped partnerships
        untapped = await self.db.execute(
            """
            SELECT COUNT(*) as count
            FROM potential_partners
            WHERE score > 0.8 AND status = 'not_contacted'
            """
        )

        if untapped.scalar() > 10:
            insights.append(StrategicInsight(
                category="Partnerships",
                severity="opportunity",
                insight=f"{untapped.scalar()} high-score partnership opportunities identified",
                impact="Potential 40% increase in deal flow",
                recommendation="Launch partnership outreach campaign this quarter",
                potential_value=2000000,
                confidence=0.75,
                data_points={"untapped_partners": untapped.scalar()}
            ))

        return insights

    async def _generate_competitive_insights(self) -> List[StrategicInsight]:
        """Generate competitive insights"""

        insights = []

        # Competitive advantage in AI
        insights.append(StrategicInsight(
            category="Competitive",
            severity="opportunity",
            insight="AI accuracy 10% higher than nearest competitor",
            impact="Defensible moat in AI-powered deal scoring",
            recommendation="Patent core AI algorithms and publicize accuracy metrics",
            potential_value=10000000,
            confidence=0.9,
            data_points={"ai_advantage": 0.1}
        ))

        return insights

    async def _generate_growth_insights(self) -> List[StrategicInsight]:
        """Generate growth insights"""

        insights = []

        # Podcast conversion opportunity
        podcast_listeners = await self.db.execute(
            """
            SELECT COUNT(DISTINCT listener_id) as listeners
            FROM podcast_analytics
            WHERE listener_id NOT IN (SELECT user_id FROM users)
            """
        )

        unconverted = podcast_listeners.scalar() or 0

        if unconverted > 1000:
            insights.append(StrategicInsight(
                category="Growth",
                severity="opportunity",
                insight=f"{unconverted} podcast listeners not yet converted to platform",
                impact=f"£{unconverted * 200:,.0f} potential MRR",
                recommendation="Launch targeted email campaign to podcast audience",
                potential_value=unconverted * 200 * 12,
                confidence=0.7,
                data_points={"unconverted_listeners": unconverted}
            ))

        return insights

    async def _generate_risk_insights(self) -> List[StrategicInsight]:
        """Generate risk insights"""

        insights = []

        # Revenue concentration risk
        concentration = await self.db.execute(
            """
            SELECT
                SUM(CASE WHEN revenue > 10000 THEN revenue ELSE 0 END) / SUM(revenue) as concentration
            FROM customer_revenue
            WHERE date >= NOW() - INTERVAL '30 days'
            """
        )

        if concentration.scalar() and concentration.scalar() > 0.5:
            insights.append(StrategicInsight(
                category="Risk",
                severity="warning",
                insight="High revenue concentration in enterprise customers",
                impact="50% of revenue from top 10% of customers",
                recommendation="Diversify revenue base with SMB segment focus",
                potential_value=-1000000,  # Negative for risk
                confidence=0.85,
                data_points={"concentration": concentration.scalar()}
            ))

        return insights

    def _assess_threat_level(self, competitor: Any) -> str:
        """Assess competitor threat level"""

        if competitor.market_share > 20:
            return "High"
        elif competitor.market_share > 10:
            return "Medium"
        else:
            return "Low"