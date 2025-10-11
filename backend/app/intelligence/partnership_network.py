"""
Partnership Network Analysis System
Relationship mapping and influence assessment for strategic partnerships
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import numpy as np
import networkx as nx
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import community as community_louvain
import structlog

logger = structlog.get_logger()


class RelationshipType(Enum):
    """Types of partnership relationships"""
    STRATEGIC_ALLIANCE = "strategic_alliance"
    CHANNEL_PARTNER = "channel_partner"
    TECHNOLOGY_PARTNER = "technology_partner"
    INVESTOR = "investor"
    ADVISOR = "advisor"
    CLIENT = "client"
    SUPPLIER = "supplier"
    COMPETITOR = "competitor"
    POTENTIAL = "potential"


class InfluenceMetric(Enum):
    """Influence measurement metrics"""
    NETWORK_REACH = "network_reach"
    DEAL_FLOW = "deal_flow"
    MARKET_ACCESS = "market_access"
    EXPERTISE = "expertise"
    CAPITAL_ACCESS = "capital_access"
    BRAND_VALUE = "brand_value"


@dataclass
class PartnerProfile:
    """Comprehensive partner profile"""
    partner_id: str
    name: str
    type: RelationshipType
    influence_score: float
    network_position: Dict[str, float]
    capabilities: List[str]
    track_record: Dict[str, Any]
    relationship_strength: float
    engagement_history: List[Dict[str, Any]]
    value_contribution: float
    risk_assessment: Dict[str, float]
    growth_potential: float
    strategic_fit: float


@dataclass
class NetworkOpportunity:
    """Network-based opportunity"""
    opportunity_id: str
    type: str
    source_partners: List[str]
    target_partners: List[str]
    value_potential: float
    connection_path: List[str]
    introduction_probability: float
    relationship_quality: float
    time_to_establish: int  # days
    action_plan: List[str]


class PartnershipNetworkAnalyzer:
    """Advanced partnership network analysis"""

    def __init__(self, db_session):
        self.db = db_session
        self.network = nx.DiGraph()
        self.influence_model = None
        self.relationship_predictor = RelationshipPredictor()
        self.value_calculator = PartnershipValueCalculator()
        self.network_optimizer = NetworkOptimizer()

    async def analyze_partnership_network(self) -> Dict[str, Any]:
        """Comprehensive partnership network analysis"""

        # Build network from data
        await self._build_partnership_network()

        # Perform analyses in parallel
        tasks = [
            self._analyze_network_structure(),
            self._assess_partner_influence(),
            self._identify_network_opportunities(),
            self._evaluate_relationship_health(),
            self._predict_partnership_evolution(),
            self._optimize_network_strategy()
        ]

        results = await asyncio.gather(*tasks)

        return {
            "network_structure": results[0],
            "influence_assessment": results[1],
            "opportunities": results[2],
            "relationship_health": results[3],
            "evolution_prediction": results[4],
            "optimization_strategy": results[5],
            "network_metrics": self._calculate_network_metrics(),
            "strategic_recommendations": await self._generate_recommendations(results)
        }

    async def _build_partnership_network(self) -> None:
        """Build partnership network from data"""

        # Fetch partnership data
        partnerships = await self.db.execute("""
            SELECT partner_id, partner_name, relationship_type,
                   relationship_strength, value_contribution
            FROM partnerships
            WHERE status = 'active'
        """)

        # Add nodes
        for partnership in partnerships:
            self.network.add_node(
                partnership.partner_id,
                name=partnership.partner_name,
                type=partnership.relationship_type,
                strength=partnership.relationship_strength,
                value=partnership.value_contribution
            )

        # Fetch connections between partners
        connections = await self.db.execute("""
            SELECT source_id, target_id, connection_type,
                   connection_strength, interaction_frequency
            FROM partner_connections
        """)

        # Add edges
        for conn in connections:
            self.network.add_edge(
                conn.source_id,
                conn.target_id,
                type=conn.connection_type,
                weight=conn.connection_strength,
                frequency=conn.interaction_frequency
            )

    async def _analyze_network_structure(self) -> Dict[str, Any]:
        """Analyze partnership network structure"""

        if self.network.number_of_nodes() == 0:
            return {"status": "empty_network"}

        # Basic network metrics
        structure = {
            "total_partners": self.network.number_of_nodes(),
            "total_connections": self.network.number_of_edges(),
            "network_density": nx.density(self.network),
            "avg_connections": self.network.number_of_edges() / self.network.number_of_nodes() if self.network.number_of_nodes() > 0 else 0
        }

        # Centrality analysis
        structure["centrality"] = {
            "most_connected": self._get_top_central_nodes(nx.degree_centrality(self.network)),
            "most_influential": self._get_top_central_nodes(nx.eigenvector_centrality(self.network, max_iter=1000)),
            "best_connectors": self._get_top_central_nodes(nx.betweenness_centrality(self.network))
        }

        # Community detection
        communities = self._detect_communities()
        structure["communities"] = {
            "count": len(communities),
            "sizes": [len(c) for c in communities],
            "modularity": nx.community.modularity(self.network.to_undirected(), communities)
        }

        # Network resilience
        structure["resilience"] = {
            "articulation_points": list(nx.articulation_points(self.network.to_undirected())),
            "connectivity": nx.node_connectivity(self.network),
            "redundancy": self._calculate_redundancy()
        }

        # Growth patterns
        structure["growth"] = await self._analyze_growth_patterns()

        return structure

    async def _assess_partner_influence(self) -> List[PartnerProfile]:
        """Assess influence of each partner"""

        partner_profiles = []

        for node in self.network.nodes():
            # Calculate influence metrics
            influence_metrics = {
                InfluenceMetric.NETWORK_REACH: self._calculate_network_reach(node),
                InfluenceMetric.DEAL_FLOW: await self._calculate_deal_flow_influence(node),
                InfluenceMetric.MARKET_ACCESS: await self._calculate_market_access(node),
                InfluenceMetric.EXPERTISE: await self._calculate_expertise_value(node),
                InfluenceMetric.CAPITAL_ACCESS: await self._calculate_capital_access(node),
                InfluenceMetric.BRAND_VALUE: await self._calculate_brand_value(node)
            }

            # Overall influence score
            influence_score = self._calculate_overall_influence(influence_metrics)

            # Network position metrics
            network_position = {
                "degree_centrality": nx.degree_centrality(self.network)[node],
                "betweenness_centrality": nx.betweenness_centrality(self.network)[node],
                "closeness_centrality": nx.closeness_centrality(self.network)[node],
                "eigenvector_centrality": nx.eigenvector_centrality(self.network, max_iter=1000)[node]
            }

            # Create partner profile
            profile = PartnerProfile(
                partner_id=node,
                name=self.network.nodes[node].get("name", node),
                type=RelationshipType(self.network.nodes[node].get("type", "potential")),
                influence_score=influence_score,
                network_position=network_position,
                capabilities=await self._get_partner_capabilities(node),
                track_record=await self._get_partner_track_record(node),
                relationship_strength=self.network.nodes[node].get("strength", 0),
                engagement_history=await self._get_engagement_history(node),
                value_contribution=self.network.nodes[node].get("value", 0),
                risk_assessment=await self._assess_partner_risk(node),
                growth_potential=await self._calculate_growth_potential(node),
                strategic_fit=await self._calculate_strategic_fit(node)
            )

            partner_profiles.append(profile)

        # Sort by influence score
        partner_profiles.sort(key=lambda x: x.influence_score, reverse=True)

        return partner_profiles[:50]  # Top 50 partners

    async def _identify_network_opportunities(self) -> List[NetworkOpportunity]:
        """Identify opportunities through network connections"""

        opportunities = []

        # Find bridge opportunities
        bridge_opps = await self._find_bridge_opportunities()
        opportunities.extend(bridge_opps)

        # Find cluster bridging opportunities
        cluster_opps = await self._find_cluster_opportunities()
        opportunities.extend(cluster_opps)

        # Find weak tie opportunities
        weak_tie_opps = await self._find_weak_tie_opportunities()
        opportunities.extend(weak_tie_opps)

        # Find introduction chain opportunities
        intro_opps = await self._find_introduction_opportunities()
        opportunities.extend(intro_opps)

        # Score and rank opportunities
        for opp in opportunities:
            opp.value_potential = await self.value_calculator.calculate_opportunity_value(opp)

        opportunities.sort(key=lambda x: x.value_potential, reverse=True)

        return opportunities[:20]  # Top 20 opportunities

    async def _evaluate_relationship_health(self) -> Dict[str, Any]:
        """Evaluate health of partner relationships"""

        health_assessment = {
            "overall_health": 0,
            "at_risk_relationships": [],
            "strong_relationships": [],
            "improvement_opportunities": [],
            "relationship_distribution": {}
        }

        total_health = 0
        relationship_count = 0

        for node in self.network.nodes():
            # Calculate relationship health score
            health_score = await self._calculate_relationship_health(node)

            total_health += health_score
            relationship_count += 1

            # Categorize relationships
            if health_score < 0.3:
                health_assessment["at_risk_relationships"].append({
                    "partner": node,
                    "health_score": health_score,
                    "issues": await self._identify_relationship_issues(node),
                    "recommendations": await self._generate_relationship_recommendations(node)
                })
            elif health_score > 0.8:
                health_assessment["strong_relationships"].append({
                    "partner": node,
                    "health_score": health_score,
                    "strengths": await self._identify_relationship_strengths(node)
                })
            elif health_score < 0.6:
                health_assessment["improvement_opportunities"].append({
                    "partner": node,
                    "health_score": health_score,
                    "improvement_areas": await self._identify_improvement_areas(node)
                })

        # Calculate overall health
        health_assessment["overall_health"] = total_health / relationship_count if relationship_count > 0 else 0

        # Relationship distribution
        health_assessment["relationship_distribution"] = {
            "strong": len(health_assessment["strong_relationships"]),
            "healthy": relationship_count - len(health_assessment["at_risk_relationships"]) - len(health_assessment["strong_relationships"]),
            "at_risk": len(health_assessment["at_risk_relationships"])
        }

        return health_assessment

    async def _predict_partnership_evolution(self) -> Dict[str, Any]:
        """Predict how partnerships will evolve"""

        predictions = {
            "growth_predictions": [],
            "churn_risks": [],
            "upgrade_opportunities": [],
            "network_evolution": {}
        }

        # Predict individual partnership evolution
        for node in self.network.nodes():
            evolution = await self.relationship_predictor.predict_evolution(
                node,
                self.network,
                self.db
            )

            if evolution["growth_probability"] > 0.7:
                predictions["growth_predictions"].append({
                    "partner": node,
                    "growth_probability": evolution["growth_probability"],
                    "predicted_value_increase": evolution["value_increase"],
                    "timeline": evolution["timeline"]
                })

            if evolution["churn_risk"] > 0.5:
                predictions["churn_risks"].append({
                    "partner": node,
                    "churn_risk": evolution["churn_risk"],
                    "risk_factors": evolution["risk_factors"],
                    "retention_strategies": evolution["retention_strategies"]
                })

            if evolution["upgrade_potential"] > 0.6:
                predictions["upgrade_opportunities"].append({
                    "partner": node,
                    "current_type": self.network.nodes[node].get("type"),
                    "upgrade_to": evolution["upgrade_type"],
                    "value_increase": evolution["upgrade_value"]
                })

        # Predict network-level evolution
        predictions["network_evolution"] = {
            "predicted_size": await self._predict_network_size(),
            "predicted_density": await self._predict_network_density(),
            "emerging_clusters": await self._predict_emerging_clusters(),
            "strategic_shifts": await self._predict_strategic_shifts()
        }

        return predictions

    async def _optimize_network_strategy(self) -> Dict[str, Any]:
        """Optimize partnership network strategy"""

        optimization = await self.network_optimizer.optimize(
            self.network,
            objectives={
                "maximize_influence": 0.3,
                "maximize_deal_flow": 0.3,
                "minimize_risk": 0.2,
                "maximize_diversity": 0.2
            }
        )

        strategy = {
            "recommended_additions": optimization["add_partners"],
            "recommended_removals": optimization["remove_partners"],
            "relationship_upgrades": optimization["upgrade_relationships"],
            "resource_allocation": optimization["resource_allocation"],
            "expected_improvement": optimization["expected_improvement"],
            "implementation_plan": self._create_implementation_plan(optimization)
        }

        return strategy

    def _calculate_network_metrics(self) -> Dict[str, float]:
        """Calculate comprehensive network metrics"""

        if self.network.number_of_nodes() == 0:
            return {}

        metrics = {
            "average_path_length": nx.average_shortest_path_length(self.network) if nx.is_strongly_connected(self.network) else 0,
            "clustering_coefficient": nx.average_clustering(self.network.to_undirected()),
            "network_diameter": nx.diameter(self.network) if nx.is_strongly_connected(self.network) else 0,
            "edge_connectivity": nx.edge_connectivity(self.network),
            "node_connectivity": nx.node_connectivity(self.network),
            "assortativity": nx.degree_assortativity_coefficient(self.network),
            "reciprocity": nx.reciprocity(self.network),
            "transitivity": nx.transitivity(self.network)
        }

        return metrics

    def _get_top_central_nodes(self, centrality_dict: Dict, top_n: int = 5) -> List[Tuple[str, float]]:
        """Get top central nodes"""

        sorted_nodes = sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:top_n]

    def _detect_communities(self) -> List[Set]:
        """Detect communities in network"""

        if self.network.number_of_nodes() == 0:
            return []

        # Convert to undirected for community detection
        undirected = self.network.to_undirected()

        # Use Louvain method
        partition = community_louvain.best_partition(undirected)

        # Convert partition to list of sets
        communities = {}
        for node, comm_id in partition.items():
            if comm_id not in communities:
                communities[comm_id] = set()
            communities[comm_id].add(node)

        return list(communities.values())

    def _calculate_redundancy(self) -> float:
        """Calculate network redundancy"""

        if self.network.number_of_nodes() < 2:
            return 0

        # Calculate average number of paths between nodes
        path_counts = []

        for source in self.network.nodes():
            for target in self.network.nodes():
                if source != target:
                    try:
                        paths = list(nx.all_simple_paths(
                            self.network,
                            source,
                            target,
                            cutoff=3
                        ))
                        path_counts.append(len(paths))
                    except:
                        path_counts.append(0)

        avg_paths = sum(path_counts) / len(path_counts) if path_counts else 0

        # Normalize to 0-1 scale
        redundancy = min(avg_paths / 3, 1.0)  # 3 paths = full redundancy

        return redundancy

    async def _analyze_growth_patterns(self) -> Dict[str, Any]:
        """Analyze network growth patterns"""

        # Fetch historical network data
        history = await self.db.execute("""
            SELECT date, node_count, edge_count, avg_strength
            FROM network_history
            WHERE date >= NOW() - INTERVAL '12 months'
            ORDER BY date
        """)

        if not history:
            return {"status": "no_history"}

        # Calculate growth metrics
        growth_data = []
        for record in history:
            growth_data.append({
                "date": record.date,
                "nodes": record.node_count,
                "edges": record.edge_count,
                "avg_strength": record.avg_strength
            })

        # Calculate growth rates
        if len(growth_data) >= 2:
            node_growth = (growth_data[-1]["nodes"] - growth_data[0]["nodes"]) / growth_data[0]["nodes"] if growth_data[0]["nodes"] > 0 else 0
            edge_growth = (growth_data[-1]["edges"] - growth_data[0]["edges"]) / growth_data[0]["edges"] if growth_data[0]["edges"] > 0 else 0
        else:
            node_growth = edge_growth = 0

        return {
            "node_growth_rate": node_growth,
            "edge_growth_rate": edge_growth,
            "growth_trajectory": "accelerating" if node_growth > 0.5 else "steady" if node_growth > 0 else "declining",
            "historical_data": growth_data
        }

    def _calculate_network_reach(self, node: str) -> float:
        """Calculate network reach of a partner"""

        if node not in self.network:
            return 0

        # Calculate reachable nodes within 2 hops
        reachable = set()
        for distance in [1, 2]:
            for target in self.network.nodes():
                try:
                    if nx.shortest_path_length(self.network, node, target) <= distance:
                        reachable.add(target)
                except:
                    pass

        # Normalize by total nodes
        reach = len(reachable) / self.network.number_of_nodes() if self.network.number_of_nodes() > 0 else 0

        return reach

    async def _calculate_deal_flow_influence(self, node: str) -> float:
        """Calculate partner's influence on deal flow"""

        # Fetch deal flow data
        result = await self.db.execute("""
            SELECT COUNT(*) as deal_count,
                   SUM(deal_value) as total_value
            FROM deals
            WHERE source_partner = ?
            OR involved_partners @> ARRAY[?]
        """, (node, node))

        if result:
            # Normalize by average
            avg_deals = 10  # Average deals per partner
            influence = min(result.deal_count / avg_deals, 1.0)
            return influence

        return 0

    async def _calculate_market_access(self, node: str) -> float:
        """Calculate market access provided by partner"""

        # Fetch market access data
        result = await self.db.execute("""
            SELECT market_segments, geographic_reach,
                   customer_base_size
            FROM partner_profiles
            WHERE partner_id = ?
        """, (node,))

        if result:
            # Calculate market access score
            segments = len(result.market_segments) if result.market_segments else 0
            reach = len(result.geographic_reach) if result.geographic_reach else 0
            customers = result.customer_base_size or 0

            # Normalize and combine
            access_score = (
                min(segments / 5, 1.0) * 0.3 +
                min(reach / 10, 1.0) * 0.3 +
                min(customers / 10000, 1.0) * 0.4
            )

            return access_score

        return 0

    async def _calculate_expertise_value(self, node: str) -> float:
        """Calculate value of partner's expertise"""

        # Fetch expertise data
        result = await self.db.execute("""
            SELECT expertise_areas, certifications,
                   years_experience, thought_leadership_score
            FROM partner_profiles
            WHERE partner_id = ?
        """, (node,))

        if result:
            expertise_score = (
                min(len(result.expertise_areas) / 5, 1.0) * 0.3 +
                min(len(result.certifications) / 3, 1.0) * 0.2 +
                min(result.years_experience / 20, 1.0) * 0.2 +
                min(result.thought_leadership_score / 100, 1.0) * 0.3
            )

            return expertise_score

        return 0

    async def _calculate_capital_access(self, node: str) -> float:
        """Calculate capital access through partner"""

        # Fetch capital access data
        result = await self.db.execute("""
            SELECT funding_capacity, investment_track_record,
                   lp_network_size
            FROM partner_profiles
            WHERE partner_id = ?
        """, (node,))

        if result:
            capital_score = (
                min(result.funding_capacity / 100000000, 1.0) * 0.5 +  # £100M
                min(result.investment_track_record / 50, 1.0) * 0.3 +
                min(result.lp_network_size / 100, 1.0) * 0.2
            )

            return capital_score

        return 0

    async def _calculate_brand_value(self, node: str) -> float:
        """Calculate brand value of partner"""

        # Fetch brand value data
        result = await self.db.execute("""
            SELECT brand_recognition, media_presence,
                   industry_awards, nps_score
            FROM partner_profiles
            WHERE partner_id = ?
        """, (node,))

        if result:
            brand_score = (
                min(result.brand_recognition / 100, 1.0) * 0.4 +
                min(result.media_presence / 100, 1.0) * 0.2 +
                min(result.industry_awards / 10, 1.0) * 0.2 +
                min(result.nps_score / 100, 1.0) * 0.2
            )

            return brand_score

        return 0

    def _calculate_overall_influence(self, metrics: Dict[InfluenceMetric, float]) -> float:
        """Calculate overall influence score"""

        weights = {
            InfluenceMetric.NETWORK_REACH: 0.2,
            InfluenceMetric.DEAL_FLOW: 0.25,
            InfluenceMetric.MARKET_ACCESS: 0.2,
            InfluenceMetric.EXPERTISE: 0.15,
            InfluenceMetric.CAPITAL_ACCESS: 0.1,
            InfluenceMetric.BRAND_VALUE: 0.1
        }

        influence = sum(
            metrics.get(metric, 0) * weight
            for metric, weight in weights.items()
        )

        return min(influence, 1.0)

    async def _find_bridge_opportunities(self) -> List[NetworkOpportunity]:
        """Find opportunities to bridge disconnected components"""

        opportunities = []

        # Find weakly connected components
        components = list(nx.weakly_connected_components(self.network))

        if len(components) > 1:
            # Find potential bridges between components
            for i, comp1 in enumerate(components):
                for comp2 in components[i+1:]:
                    # Find best connection points
                    best_bridge = self._find_best_bridge(comp1, comp2)

                    if best_bridge:
                        opportunities.append(NetworkOpportunity(
                            opportunity_id=f"bridge_{datetime.utcnow().timestamp()}",
                            type="component_bridge",
                            source_partners=list(comp1)[:3],
                            target_partners=list(comp2)[:3],
                            value_potential=0,  # Will be calculated
                            connection_path=best_bridge["path"],
                            introduction_probability=best_bridge["probability"],
                            relationship_quality=0.5,
                            time_to_establish=90,
                            action_plan=[
                                "Identify mutual connections",
                                "Arrange introduction",
                                "Facilitate initial engagement",
                                "Build sustained relationship"
                            ]
                        ))

        return opportunities

    def _find_best_bridge(self, comp1: Set, comp2: Set) -> Optional[Dict[str, Any]]:
        """Find best bridge between components"""

        # Simplified bridge finding
        # In production would use more sophisticated algorithm

        return {
            "path": [list(comp1)[0], "intermediate", list(comp2)[0]],
            "probability": 0.6
        }

    async def _find_cluster_opportunities(self) -> List[NetworkOpportunity]:
        """Find opportunities between clusters"""

        opportunities = []

        # Detect clusters
        clusters = self._detect_communities()

        # Find inter-cluster opportunities
        for i, cluster1 in enumerate(clusters):
            for cluster2 in clusters[i+1:]:
                # Check existing connections
                connections = 0
                for node1 in cluster1:
                    for node2 in cluster2:
                        if self.network.has_edge(node1, node2):
                            connections += 1

                # If under-connected, create opportunity
                if connections < len(cluster1) * len(cluster2) * 0.1:  # Less than 10% connected
                    opportunities.append(NetworkOpportunity(
                        opportunity_id=f"cluster_{datetime.utcnow().timestamp()}",
                        type="cluster_bridge",
                        source_partners=list(cluster1)[:3],
                        target_partners=list(cluster2)[:3],
                        value_potential=0,
                        connection_path=[],
                        introduction_probability=0.7,
                        relationship_quality=0.6,
                        time_to_establish=60,
                        action_plan=[
                            "Identify cluster synergies",
                            "Create joint initiatives",
                            "Facilitate cross-cluster collaboration"
                        ]
                    ))

        return opportunities

    async def _find_weak_tie_opportunities(self) -> List[NetworkOpportunity]:
        """Find opportunities through weak ties"""

        opportunities = []

        # Find weak ties (low weight edges)
        weak_ties = [
            (u, v) for u, v, d in self.network.edges(data=True)
            if d.get("weight", 1) < 0.3
        ]

        for source, target in weak_ties[:10]:  # Top 10 weak ties
            opportunities.append(NetworkOpportunity(
                opportunity_id=f"weak_tie_{datetime.utcnow().timestamp()}",
                type="strengthen_weak_tie",
                source_partners=[source],
                target_partners=[target],
                value_potential=0,
                connection_path=[source, target],
                introduction_probability=1.0,  # Already connected
                relationship_quality=0.3,
                time_to_establish=30,
                action_plan=[
                    "Increase engagement frequency",
                    "Identify collaboration opportunities",
                    "Strengthen relationship"
                ]
            ))

        return opportunities

    async def _find_introduction_opportunities(self) -> List[NetworkOpportunity]:
        """Find introduction chain opportunities"""

        opportunities = []

        # Find high-value targets not directly connected
        high_value_targets = await self.db.execute("""
            SELECT partner_id, value_score
            FROM partner_profiles
            WHERE value_score > 0.8
            AND partner_id NOT IN (
                SELECT target_id FROM partner_connections
                WHERE source_id = 'our_company'
            )
            LIMIT 10
        """)

        for target in high_value_targets:
            # Find shortest path to target
            try:
                path = nx.shortest_path(self.network, "our_company", target.partner_id)

                if len(path) > 2 and len(path) <= 4:  # 2-3 degrees of separation
                    opportunities.append(NetworkOpportunity(
                        opportunity_id=f"introduction_{datetime.utcnow().timestamp()}",
                        type="introduction_chain",
                        source_partners=["our_company"],
                        target_partners=[target.partner_id],
                        value_potential=target.value_score * 100,  # £100M * score
                        connection_path=path,
                        introduction_probability=0.8 ** (len(path) - 2),  # Decay with distance
                        relationship_quality=0.5,
                        time_to_establish=30 * (len(path) - 1),
                        action_plan=[
                            f"Connect through {path[1]}",
                            "Request introduction",
                            "Build relationship gradually"
                        ]
                    ))
            except:
                pass  # No path exists

        return opportunities

    async def _generate_recommendations(self, analysis_results: List) -> List[Dict[str, Any]]:
        """Generate strategic recommendations"""

        recommendations = []

        # Network structure recommendations
        structure = analysis_results[0]
        if structure.get("network_density", 0) < 0.1:
            recommendations.append({
                "priority": "High",
                "category": "Network Density",
                "recommendation": "Increase network connections",
                "action": "Facilitate more partner-to-partner connections",
                "expected_impact": "25% improvement in deal flow"
            })

        # Influence recommendations
        influence = analysis_results[1]
        if influence:
            top_influencer = influence[0]
            recommendations.append({
                "priority": "High",
                "category": "Key Relationships",
                "recommendation": f"Strengthen relationship with {top_influencer.name}",
                "action": "Increase engagement and collaboration",
                "expected_impact": f"Access to {top_influencer.network_position['degree_centrality']*100:.0f}% of network"
            })

        # Opportunity recommendations
        opportunities = analysis_results[2]
        if opportunities:
            best_opp = opportunities[0]
            recommendations.append({
                "priority": "Medium",
                "category": "Growth Opportunity",
                "recommendation": f"Pursue {best_opp.type} opportunity",
                "action": best_opp.action_plan[0],
                "expected_impact": f"£{best_opp.value_potential:.1f}M potential value"
            })

        return recommendations


class RelationshipPredictor:
    """Predict partnership relationship evolution"""

    def __init__(self):
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()

    async def predict_evolution(
        self,
        partner_id: str,
        network: nx.DiGraph,
        db
    ) -> Dict[str, Any]:
        """Predict how relationship will evolve"""

        # Extract features
        features = await self._extract_features(partner_id, network, db)

        # Make predictions (simplified - in production would use trained model)
        predictions = {
            "growth_probability": self._predict_growth(features),
            "value_increase": self._predict_value_increase(features),
            "timeline": self._predict_timeline(features),
            "churn_risk": self._predict_churn(features),
            "risk_factors": self._identify_risks(features),
            "retention_strategies": self._suggest_retention(features),
            "upgrade_potential": self._predict_upgrade(features),
            "upgrade_type": self._predict_upgrade_type(features),
            "upgrade_value": self._predict_upgrade_value(features)
        }

        return predictions

    async def _extract_features(self, partner_id: str, network: nx.DiGraph, db) -> np.ndarray:
        """Extract features for prediction"""

        features = []

        # Network features
        if partner_id in network:
            features.extend([
                network.degree(partner_id),
                network.in_degree(partner_id),
                network.out_degree(partner_id),
                nx.clustering(network.to_undirected(), partner_id)
            ])
        else:
            features.extend([0, 0, 0, 0])

        # Relationship features from database
        result = await db.execute("""
            SELECT relationship_duration, interaction_frequency,
                   value_generated, satisfaction_score
            FROM partner_relationships
            WHERE partner_id = ?
        """, (partner_id,))

        if result:
            features.extend([
                result.relationship_duration or 0,
                result.interaction_frequency or 0,
                result.value_generated or 0,
                result.satisfaction_score or 0
            ])
        else:
            features.extend([0, 0, 0, 0])

        return np.array(features)

    def _predict_growth(self, features: np.ndarray) -> float:
        """Predict growth probability"""

        # Simplified prediction logic
        # High interaction + high value = high growth probability

        if len(features) >= 8:
            interaction = features[5]  # interaction_frequency
            value = features[6]  # value_generated

            growth_prob = min((interaction * 0.5 + value * 0.5) / 100, 1.0)
            return growth_prob

        return 0.5

    def _predict_value_increase(self, features: np.ndarray) -> float:
        """Predict value increase"""

        # Simplified - predict 20-50% increase based on features
        return np.random.uniform(0.2, 0.5)

    def _predict_timeline(self, features: np.ndarray) -> int:
        """Predict timeline for evolution"""

        # Simplified - 3-12 months
        return np.random.randint(3, 13)

    def _predict_churn(self, features: np.ndarray) -> float:
        """Predict churn risk"""

        if len(features) >= 8:
            satisfaction = features[7]  # satisfaction_score
            interaction = features[5]  # interaction_frequency

            # Low satisfaction or interaction = high churn risk
            churn_risk = 1.0 - (satisfaction * 0.6 + interaction * 0.4) / 100
            return max(0, min(churn_risk, 1.0))

        return 0.3

    def _identify_risks(self, features: np.ndarray) -> List[str]:
        """Identify risk factors"""

        risks = []

        if len(features) >= 8:
            if features[5] < 10:  # Low interaction
                risks.append("Low engagement frequency")
            if features[7] < 50:  # Low satisfaction
                risks.append("Below average satisfaction")
            if features[6] < 10000:  # Low value
                risks.append("Limited value generation")

        return risks

    def _suggest_retention(self, features: np.ndarray) -> List[str]:
        """Suggest retention strategies"""

        strategies = []

        if len(features) >= 8:
            if features[5] < 10:  # Low interaction
                strategies.append("Increase touchpoint frequency")
            if features[7] < 50:  # Low satisfaction
                strategies.append("Address satisfaction concerns")
            if features[6] < 10000:  # Low value
                strategies.append("Identify new value creation opportunities")

        return strategies

    def _predict_upgrade(self, features: np.ndarray) -> float:
        """Predict upgrade potential"""

        if len(features) >= 8:
            # High value + high satisfaction = upgrade potential
            value = features[6]
            satisfaction = features[7]

            upgrade_potential = (value * 0.6 + satisfaction * 0.4) / 100
            return min(upgrade_potential, 1.0)

        return 0.3

    def _predict_upgrade_type(self, features: np.ndarray) -> str:
        """Predict type of upgrade"""

        # Simplified logic
        if features[6] > 50000:  # High value
            return "strategic_alliance"
        elif features[5] > 20:  # High interaction
            return "preferred_partner"
        else:
            return "standard_partner"

    def _predict_upgrade_value(self, features: np.ndarray) -> float:
        """Predict value from upgrade"""

        # Simplified - 50-200% increase
        return features[6] * np.random.uniform(1.5, 3.0) if len(features) >= 7 else 0


class PartnershipValueCalculator:
    """Calculate partnership opportunity values"""

    async def calculate_opportunity_value(self, opportunity: NetworkOpportunity) -> float:
        """Calculate value of network opportunity"""

        base_value = 10.0  # £10M base

        # Adjust by opportunity type
        type_multipliers = {
            "component_bridge": 3.0,
            "cluster_bridge": 2.5,
            "strengthen_weak_tie": 1.5,
            "introduction_chain": 2.0
        }

        multiplier = type_multipliers.get(opportunity.type, 1.0)

        # Adjust by probability
        value = base_value * multiplier * opportunity.introduction_probability

        # Adjust by relationship quality
        value *= opportunity.relationship_quality

        # Adjust by time to establish (prefer quicker)
        time_factor = 1.0 / (1 + opportunity.time_to_establish / 100)
        value *= time_factor

        return value


class NetworkOptimizer:
    """Optimize partnership network structure"""

    async def optimize(
        self,
        network: nx.DiGraph,
        objectives: Dict[str, float]
    ) -> Dict[str, Any]:
        """Optimize network based on objectives"""

        optimization_result = {
            "add_partners": [],
            "remove_partners": [],
            "upgrade_relationships": [],
            "resource_allocation": {},
            "expected_improvement": {}
        }

        # Identify partners to add
        optimization_result["add_partners"] = await self._identify_additions(network, objectives)

        # Identify underperforming partners
        optimization_result["remove_partners"] = await self._identify_removals(network, objectives)

        # Identify relationships to upgrade
        optimization_result["upgrade_relationships"] = await self._identify_upgrades(network, objectives)

        # Optimize resource allocation
        optimization_result["resource_allocation"] = self._optimize_resources(network, objectives)

        # Calculate expected improvement
        optimization_result["expected_improvement"] = self._calculate_improvement(
            network,
            optimization_result,
            objectives
        )

        return optimization_result

    async def _identify_additions(
        self,
        network: nx.DiGraph,
        objectives: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify partners to add"""

        additions = []

        # Simplified logic - identify gaps
        if objectives.get("maximize_influence", 0) > 0.5:
            additions.append({
                "type": "influencer",
                "profile": "Industry thought leader",
                "expected_value": 50.0,
                "cost": 10.0
            })

        if objectives.get("maximize_deal_flow", 0) > 0.5:
            additions.append({
                "type": "deal_source",
                "profile": "M&A advisor network",
                "expected_value": 75.0,
                "cost": 15.0
            })

        return additions

    async def _identify_removals(
        self,
        network: nx.DiGraph,
        objectives: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify underperforming partners"""

        removals = []

        # Identify low-value, high-risk partners
        for node in network.nodes():
            value = network.nodes[node].get("value", 0)
            risk = network.nodes[node].get("risk", 0)

            if value < 10 and risk > 0.7:
                removals.append({
                    "partner": node,
                    "reason": "Low value, high risk",
                    "value_loss": value,
                    "risk_reduction": risk
                })

        return removals[:5]  # Limit to 5 removals

    async def _identify_upgrades(
        self,
        network: nx.DiGraph,
        objectives: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify relationships to upgrade"""

        upgrades = []

        # Find high-potential relationships
        for node in network.nodes():
            potential = network.nodes[node].get("growth_potential", 0)
            current_strength = network.nodes[node].get("strength", 0)

            if potential > 0.7 and current_strength < 0.5:
                upgrades.append({
                    "partner": node,
                    "current_strength": current_strength,
                    "target_strength": 0.8,
                    "investment_required": 5.0,
                    "expected_return": 25.0
                })

        return upgrades[:10]  # Top 10 upgrades

    def _optimize_resources(
        self,
        network: nx.DiGraph,
        objectives: Dict[str, float]
    ) -> Dict[str, float]:
        """Optimize resource allocation across partners"""

        total_resources = 100.0  # £100M to allocate

        allocation = {}

        # Simple proportional allocation based on value
        total_value = sum(network.nodes[n].get("value", 0) for n in network.nodes())

        for node in network.nodes():
            node_value = network.nodes[node].get("value", 0)
            allocation[node] = (node_value / total_value) * total_resources if total_value > 0 else 0

        return allocation

    def _calculate_improvement(
        self,
        network: nx.DiGraph,
        optimization: Dict[str, Any],
        objectives: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate expected improvement from optimization"""

        improvements = {}

        # Estimate influence improvement
        influence_improvement = len(optimization["add_partners"]) * 0.1
        improvements["influence"] = influence_improvement

        # Estimate deal flow improvement
        deal_flow_improvement = (
            len(optimization["add_partners"]) * 0.15 +
            len(optimization["upgrade_relationships"]) * 0.05
        )
        improvements["deal_flow"] = deal_flow_improvement

        # Estimate risk reduction
        risk_reduction = len(optimization["remove_partners"]) * 0.05
        improvements["risk_reduction"] = risk_reduction

        return improvements