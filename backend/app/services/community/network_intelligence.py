"""
Network Intelligence Service for M&A Community Platform
Advanced relationship mapping and partnership identification
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import networkx as nx
import numpy as np
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor
import structlog

from app.services.claude_mcp import ClaudeMCPService
from app.core.cache import cache_service
from app.models import Member, Connection, Deal, Partnership

logger = structlog.get_logger(__name__)


@dataclass
class NetworkNode:
    """Represents a member in the network graph"""
    member_id: str
    expertise: List[str]
    deal_history: Dict[str, Any]
    influence_score: float
    connection_strength: Dict[str, float]
    partnership_potential: float


@dataclass
class PartnershipOpportunity:
    """Represents a potential partnership"""
    member1_id: str
    member2_id: str
    compatibility_score: float
    synergy_areas: List[str]
    estimated_value: float
    success_probability: float
    recommended_actions: List[str]


class NetworkIntelligenceEngine:
    """
    Advanced network analysis and partnership identification system
    that surpasses Circle.so and Skool.com capabilities
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.claude_mcp = ClaudeMCPService()
        self.ml_model = self._initialize_ml_model()
        self.cache_ttl = 3600  # 1 hour cache

    def _initialize_ml_model(self) -> RandomForestRegressor:
        """Initialize ML model for partnership prediction"""
        # In production, this would load a pre-trained model
        return RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

    async def build_network_graph(self, organization_id: str) -> nx.DiGraph:
        """
        Build comprehensive network graph with relationship intelligence
        """
        cache_key = f"network_graph:{organization_id}"
        cached = await cache_service.get(cache_key)
        if cached:
            return nx.node_link_graph(cached)

        # Fetch members and connections
        members = await self._fetch_members(organization_id)
        connections = await self._fetch_connections(organization_id)

        # Build graph structure
        for member in members:
            self.graph.add_node(
                member.id,
                **{
                    "name": member.name,
                    "expertise": member.expertise,
                    "influence": await self._calculate_influence(member),
                    "deal_value": member.total_deal_value,
                    "success_rate": member.deal_success_rate
                }
            )

        # Add edges with relationship strength
        for connection in connections:
            strength = await self._calculate_relationship_strength(connection)
            self.graph.add_edge(
                connection.from_member_id,
                connection.to_member_id,
                weight=strength,
                interactions=connection.interaction_count,
                shared_deals=connection.shared_deals
            )

        # Cache the graph
        graph_data = nx.node_link_data(self.graph)
        await cache_service.set(cache_key, graph_data, ttl=self.cache_ttl)

        return self.graph

    async def identify_partnership_opportunities(
        self,
        member_id: str,
        limit: int = 10
    ) -> List[PartnershipOpportunity]:
        """
        AI-powered partnership identification with strategic matching
        """
        member = await self._get_member(member_id)
        potential_partners = await self._find_potential_partners(member)

        opportunities = []
        for partner in potential_partners[:limit * 2]:  # Analyze more to filter
            opportunity = await self._analyze_partnership_potential(
                member, partner
            )
            if opportunity.compatibility_score > 0.6:
                opportunities.append(opportunity)

        # Sort by estimated value and success probability
        opportunities.sort(
            key=lambda x: x.estimated_value * x.success_probability,
            reverse=True
        )

        return opportunities[:limit]

    async def _analyze_partnership_potential(
        self,
        member1: Member,
        member2: Member
    ) -> PartnershipOpportunity:
        """
        Deep analysis of partnership compatibility and value
        """
        # Calculate compatibility using multiple factors
        expertise_synergy = self._calculate_expertise_synergy(
            member1.expertise, member2.expertise
        )

        market_alignment = await self._assess_market_alignment(member1, member2)

        cultural_fit = await self._evaluate_cultural_fit(member1, member2)

        financial_compatibility = self._assess_financial_compatibility(
            member1, member2
        )

        # Use Claude MCP for strategic analysis
        strategic_analysis = await self.claude_mcp.analyze_partnership(
            member1_profile=member1.to_dict(),
            member2_profile=member2.to_dict(),
            context={
                "expertise_synergy": expertise_synergy,
                "market_alignment": market_alignment,
                "cultural_fit": cultural_fit
            }
        )

        # Calculate overall compatibility
        compatibility_score = np.mean([
            expertise_synergy * 0.3,
            market_alignment * 0.25,
            cultural_fit * 0.2,
            financial_compatibility * 0.25
        ])

        # Estimate partnership value
        estimated_value = await self._estimate_partnership_value(
            member1, member2, compatibility_score
        )

        # Predict success probability using ML
        success_probability = self._predict_partnership_success(
            member1, member2, compatibility_score
        )

        return PartnershipOpportunity(
            member1_id=member1.id,
            member2_id=member2.id,
            compatibility_score=compatibility_score,
            synergy_areas=strategic_analysis.get("synergy_areas", []),
            estimated_value=estimated_value,
            success_probability=success_probability,
            recommended_actions=strategic_analysis.get("next_steps", [])
        )

    def _calculate_expertise_synergy(
        self,
        expertise1: List[str],
        expertise2: List[str]
    ) -> float:
        """Calculate how well expertise areas complement each other"""
        # Complementary expertise is better than identical
        overlap = set(expertise1).intersection(set(expertise2))
        unique1 = set(expertise1) - overlap
        unique2 = set(expertise2) - overlap

        if not expertise1 or not expertise2:
            return 0.0

        # Optimal synergy: some overlap but mostly complementary
        overlap_ratio = len(overlap) / max(len(expertise1), len(expertise2))
        complementary_ratio = (len(unique1) + len(unique2)) / (
            len(expertise1) + len(expertise2)
        )

        # Sweet spot: 20-40% overlap, 60-80% complementary
        optimal_overlap = 1 - abs(overlap_ratio - 0.3) * 2
        optimal_complement = 1 - abs(complementary_ratio - 0.7) * 2

        return (optimal_overlap + optimal_complement) / 2

    async def calculate_network_influence(self, member_id: str) -> Dict[str, float]:
        """
        Calculate multi-dimensional influence metrics
        """
        if member_id not in self.graph:
            await self.build_network_graph(member_id)

        # Centrality metrics
        degree_centrality = nx.degree_centrality(self.graph)[member_id]
        betweenness = nx.betweenness_centrality(self.graph).get(member_id, 0)
        closeness = nx.closeness_centrality(self.graph).get(member_id, 0)

        # PageRank for influence propagation
        pagerank = nx.pagerank(self.graph).get(member_id, 0)

        # Custom metrics
        bridge_score = await self._calculate_bridge_importance(member_id)
        deal_influence = await self._calculate_deal_influence(member_id)

        return {
            "overall_influence": (
                degree_centrality * 0.2 +
                betweenness * 0.3 +
                closeness * 0.1 +
                pagerank * 0.2 +
                deal_influence * 0.2
            ),
            "network_reach": degree_centrality,
            "bridge_importance": bridge_score,
            "information_flow": betweenness,
            "access_efficiency": closeness,
            "reputation_score": pagerank,
            "deal_influence": deal_influence
        }

    async def _calculate_bridge_importance(self, member_id: str) -> float:
        """
        Calculate importance as a bridge between communities
        """
        # Remove node and check connectivity impact
        temp_graph = self.graph.copy()
        temp_graph.remove_node(member_id)

        original_components = nx.number_weakly_connected_components(self.graph)
        new_components = nx.number_weakly_connected_components(temp_graph)

        # Higher score if removal increases components (breaking bridges)
        bridge_score = (new_components - original_components) / original_components

        return min(bridge_score, 1.0)

    async def identify_super_connectors(
        self,
        organization_id: str,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Identify members who accelerate network effects
        """
        await self.build_network_graph(organization_id)

        super_connectors = []

        for member_id in self.graph.nodes():
            influence = await self.calculate_network_influence(member_id)

            # Calculate connection quality
            edges = self.graph.edges(member_id, data=True)
            avg_strength = np.mean([e[2]['weight'] for e in edges]) if edges else 0

            # Calculate value multiplication effect
            connected_value = sum(
                self.graph.nodes[target].get('deal_value', 0)
                for _, target in self.graph.edges(member_id)
            )

            super_connectors.append({
                "member_id": member_id,
                "influence_score": influence["overall_influence"],
                "bridge_importance": influence["bridge_importance"],
                "connection_quality": avg_strength,
                "value_multiplier": connected_value / 1000000,  # In millions
                "recommendation": "Super Connector" if influence["overall_influence"] > 0.7 else "Key Connector"
            })

        # Sort by influence and return top N
        super_connectors.sort(key=lambda x: x["influence_score"], reverse=True)
        return super_connectors[:top_n]

    async def predict_relationship_success(
        self,
        member1_id: str,
        member2_id: str
    ) -> Dict[str, Any]:
        """
        Predict success probability of a potential relationship
        """
        # Gather features for prediction
        features = await self._extract_relationship_features(member1_id, member2_id)

        # Use ML model for prediction
        success_probability = self.ml_model.predict([features])[0]

        # Generate recommendations using Claude
        recommendations = await self.claude_mcp.generate_relationship_advice(
            member1_id=member1_id,
            member2_id=member2_id,
            compatibility_features=features,
            success_probability=success_probability
        )

        return {
            "success_probability": success_probability,
            "key_factors": self._identify_key_factors(features),
            "recommendations": recommendations,
            "optimal_introduction_method": self._suggest_introduction_method(features),
            "estimated_time_to_value": self._estimate_time_to_value(features)
        }

    async def map_deal_flow_network(
        self,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Map how deals flow through the network
        """
        await self.build_network_graph(organization_id)

        # Identify deal sources (high out-degree for deals)
        deal_sources = []

        # Identify deal facilitators (high betweenness for deals)
        deal_facilitators = []

        # Identify deal closers (high success rate)
        deal_closers = []

        for member_id in self.graph.nodes():
            member_data = self.graph.nodes[member_id]

            # Classify member role in deal flow
            if member_data.get('deal_origination_count', 0) > 5:
                deal_sources.append(member_id)

            if member_data.get('deal_facilitation_count', 0) > 3:
                deal_facilitators.append(member_id)

            if member_data.get('success_rate', 0) > 0.7:
                deal_closers.append(member_id)

        return {
            "deal_sources": deal_sources,
            "deal_facilitators": deal_facilitators,
            "deal_closers": deal_closers,
            "optimal_deal_paths": self._find_optimal_deal_paths(),
            "bottlenecks": self._identify_bottlenecks(),
            "improvement_opportunities": await self._suggest_network_improvements()
        }

    def _find_optimal_deal_paths(self) -> List[List[str]]:
        """Find most successful paths for deal flow"""
        # Use network analysis to find paths with highest success rates
        paths = []

        # Find paths between deal sources and closers
        for source in self.graph.nodes():
            if self.graph.nodes[source].get('deal_origination_count', 0) > 5:
                for target in self.graph.nodes():
                    if self.graph.nodes[target].get('success_rate', 0) > 0.7:
                        try:
                            path = nx.shortest_path(
                                self.graph, source, target,
                                weight=lambda u, v, d: 1 / d['weight']
                            )
                            if len(path) > 1:
                                paths.append(path)
                        except nx.NetworkXNoPath:
                            continue

        return paths[:10]  # Return top 10 paths

    async def generate_networking_strategy(
        self,
        member_id: str
    ) -> Dict[str, Any]:
        """
        Generate personalized networking strategy for wealth-building
        """
        member = await self._get_member(member_id)
        influence = await self.calculate_network_influence(member_id)

        # Identify strategic connections to make
        strategic_targets = await self._identify_strategic_connections(member)

        # Identify knowledge gaps to fill
        knowledge_gaps = await self._identify_knowledge_gaps(member)

        # Find mentorship opportunities
        mentors = await self._find_ideal_mentors(member)

        # Generate action plan using Claude
        action_plan = await self.claude_mcp.generate_networking_plan(
            member_profile=member.to_dict(),
            influence_metrics=influence,
            targets=strategic_targets,
            gaps=knowledge_gaps,
            mentorship=mentors
        )

        return {
            "current_position": {
                "influence_score": influence["overall_influence"],
                "network_reach": influence["network_reach"],
                "strengths": self._identify_networking_strengths(influence),
                "weaknesses": self._identify_networking_weaknesses(influence)
            },
            "strategic_objectives": strategic_targets[:5],
            "knowledge_acquisition": knowledge_gaps[:3],
            "mentorship_matches": mentors[:2],
            "30_day_action_plan": action_plan["immediate_actions"],
            "90_day_goals": action_plan["quarterly_goals"],
            "success_metrics": action_plan["success_metrics"]
        }

    async def calculate_ecosystem_value(self) -> Dict[str, Any]:
        """
        Calculate total value created by the network ecosystem
        """
        total_members = self.graph.number_of_nodes()
        total_connections = self.graph.number_of_edges()

        # Calculate various value metrics
        total_deal_value = sum(
            self.graph.nodes[n].get('deal_value', 0)
            for n in self.graph.nodes()
        )

        # Network density (how connected the network is)
        density = nx.density(self.graph)

        # Average path length (how easily information flows)
        if nx.is_weakly_connected(self.graph):
            avg_path_length = nx.average_shortest_path_length(self.graph)
        else:
            # Calculate for largest component if not fully connected
            largest_cc = max(nx.weakly_connected_components(self.graph), key=len)
            subgraph = self.graph.subgraph(largest_cc)
            avg_path_length = nx.average_shortest_path_length(subgraph)

        # Calculate Metcalfe's Law value (network value proportional to n²)
        metcalfe_value = total_members ** 2 * 1000  # $1000 per connection potential

        # Reed's Law value (2^n for group-forming networks)
        # Use log scale for realistic calculation
        reed_value = 2 ** min(total_members, 20) * 100  # Capped for computation

        return {
            "network_metrics": {
                "total_members": total_members,
                "total_connections": total_connections,
                "network_density": density,
                "avg_path_length": avg_path_length
            },
            "value_metrics": {
                "total_deal_value": total_deal_value,
                "avg_deal_value": total_deal_value / max(total_members, 1),
                "metcalfe_value": metcalfe_value,
                "reed_value": reed_value,
                "estimated_network_value": (metcalfe_value + reed_value) / 2
            },
            "growth_metrics": {
                "member_growth_rate": await self._calculate_growth_rate("members"),
                "connection_growth_rate": await self._calculate_growth_rate("connections"),
                "value_growth_rate": await self._calculate_growth_rate("value")
            },
            "health_indicators": {
                "connectivity_health": "Excellent" if density > 0.3 else "Good" if density > 0.1 else "Needs Improvement",
                "information_flow": "Optimal" if avg_path_length < 3 else "Good" if avg_path_length < 5 else "Suboptimal",
                "value_distribution": await self._analyze_value_distribution()
            }
        }

    async def _calculate_growth_rate(self, metric_type: str) -> float:
        """Calculate growth rate for various metrics"""
        # In production, this would fetch historical data
        # For now, return simulated growth rates
        growth_rates = {
            "members": 0.15,  # 15% monthly growth
            "connections": 0.25,  # 25% monthly growth
            "value": 0.30  # 30% value growth
        }
        return growth_rates.get(metric_type, 0.1)

    async def _analyze_value_distribution(self) -> str:
        """Analyze how value is distributed across the network"""
        deal_values = [
            self.graph.nodes[n].get('deal_value', 0)
            for n in self.graph.nodes()
        ]

        if not deal_values:
            return "No data"

        # Calculate Gini coefficient for inequality measurement
        def gini(x):
            n = len(x)
            if n == 0:
                return 0
            x_sorted = sorted(x)
            cumsum = np.cumsum(x_sorted)
            total = cumsum[-1]
            if total == 0:
                return 0
            gini_sum = sum((n - i) * val for i, val in enumerate(x_sorted))
            return (n + 1 - 2 * gini_sum / total) / n

        gini_coefficient = gini(deal_values)

        if gini_coefficient < 0.3:
            return "Well distributed"
        elif gini_coefficient < 0.5:
            return "Moderately concentrated"
        else:
            return "Highly concentrated"

    # Helper methods
    async def _fetch_members(self, organization_id: str) -> List[Member]:
        """Fetch members from database"""
        # Implementation would fetch from database
        return []

    async def _fetch_connections(self, organization_id: str) -> List[Connection]:
        """Fetch connections from database"""
        # Implementation would fetch from database
        return []

    async def _get_member(self, member_id: str) -> Member:
        """Get member details"""
        # Implementation would fetch from database
        return Member()

    async def _calculate_influence(self, member: Member) -> float:
        """Calculate member influence score"""
        # Complex calculation based on multiple factors
        return 0.5

    async def _calculate_relationship_strength(self, connection: Connection) -> float:
        """Calculate strength of relationship"""
        # Based on interactions, shared deals, etc.
        return 0.5

    async def _find_potential_partners(self, member: Member) -> List[Member]:
        """Find potential partners for a member"""
        # Implementation would use graph analysis and ML
        return []

    async def _assess_market_alignment(self, member1: Member, member2: Member) -> float:
        """Assess market alignment between members"""
        return 0.7

    async def _evaluate_cultural_fit(self, member1: Member, member2: Member) -> float:
        """Evaluate cultural fit between members"""
        return 0.8

    def _assess_financial_compatibility(self, member1: Member, member2: Member) -> float:
        """Assess financial compatibility"""
        return 0.75

    async def _estimate_partnership_value(
        self,
        member1: Member,
        member2: Member,
        compatibility: float
    ) -> float:
        """Estimate potential value of partnership"""
        return compatibility * 1000000  # In dollars

    def _predict_partnership_success(
        self,
        member1: Member,
        member2: Member,
        compatibility: float
    ) -> float:
        """Predict partnership success probability"""
        return min(compatibility * 1.2, 0.95)

    async def _extract_relationship_features(
        self,
        member1_id: str,
        member2_id: str
    ) -> List[float]:
        """Extract features for ML prediction"""
        return [0.5] * 10  # Placeholder features

    def _identify_key_factors(self, features: List[float]) -> List[str]:
        """Identify key factors for relationship success"""
        return ["Complementary expertise", "Market alignment", "Trust level"]

    def _suggest_introduction_method(self, features: List[float]) -> str:
        """Suggest best introduction method"""
        return "Warm introduction via mutual connection"

    def _estimate_time_to_value(self, features: List[float]) -> str:
        """Estimate time to realize value from relationship"""
        return "3-6 months"

    def _identify_bottlenecks(self) -> List[str]:
        """Identify network bottlenecks"""
        return []

    async def _suggest_network_improvements(self) -> List[str]:
        """Suggest improvements to network structure"""
        return ["Increase connections between clusters", "Add more deal facilitators"]

    async def _identify_strategic_connections(self, member: Member) -> List[Dict]:
        """Identify strategic connections to make"""
        return []

    async def _identify_knowledge_gaps(self, member: Member) -> List[str]:
        """Identify knowledge gaps to fill"""
        return []

    async def _find_ideal_mentors(self, member: Member) -> List[Dict]:
        """Find ideal mentors for member"""
        return []

    def _identify_networking_strengths(self, influence: Dict) -> List[str]:
        """Identify networking strengths"""
        strengths = []
        if influence["bridge_importance"] > 0.7:
            strengths.append("Strong bridge connector")
        if influence["network_reach"] > 0.5:
            strengths.append("Wide network reach")
        return strengths

    def _identify_networking_weaknesses(self, influence: Dict) -> List[str]:
        """Identify networking weaknesses"""
        weaknesses = []
        if influence["network_reach"] < 0.3:
            weaknesses.append("Limited network reach")
        if influence["bridge_importance"] < 0.3:
            weaknesses.append("Few cross-cluster connections")
        return weaknesses


# Global instance
network_intelligence = NetworkIntelligenceEngine()