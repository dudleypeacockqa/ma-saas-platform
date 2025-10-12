"""
Integration Planning & Execution Engine - Advanced post-merger integration management
Provides comprehensive integration planning, execution tracking, and optimization
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import uuid
import math
from abc import ABC, abstractmethod

# Data Models and Enums
class IntegrationType(Enum):
    FULL_INTEGRATION = "full_integration"
    PARTIAL_INTEGRATION = "partial_integration"
    STANDALONE_OPERATION = "standalone_operation"
    HYBRID_MODEL = "hybrid_model"

class IntegrationPhase(Enum):
    PLANNING = "planning"
    DAY_ONE_READINESS = "day_one_readiness"
    EARLY_INTEGRATION = "early_integration"
    OPERATIONAL_INTEGRATION = "operational_integration"
    OPTIMIZATION = "optimization"
    STABILIZATION = "stabilization"

class MilestoneStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"

class IntegrationArea(Enum):
    TECHNOLOGY = "technology"
    OPERATIONS = "operations"
    FINANCE = "finance"
    HUMAN_RESOURCES = "human_resources"
    SALES_MARKETING = "sales_marketing"
    LEGAL_COMPLIANCE = "legal_compliance"
    SUPPLY_CHAIN = "supply_chain"
    CUSTOMER_SERVICE = "customer_service"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class IntegrationMilestone:
    """Individual integration milestone"""
    milestone_id: str
    name: str
    description: str
    integration_area: IntegrationArea
    phase: IntegrationPhase
    status: MilestoneStatus = MilestoneStatus.NOT_STARTED
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    owner: Optional[str] = None
    team_members: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    completion_percentage: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    risk_factors: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)

@dataclass
class IntegrationPlan:
    """Comprehensive integration plan"""
    plan_id: str
    deal_id: str
    integration_type: IntegrationType
    target_company: str
    acquirer_company: str
    planned_completion_date: datetime
    milestones: List[IntegrationMilestone] = field(default_factory=list)
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    budget_allocation: Dict[str, float] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class IntegrationProgress:
    """Real-time integration progress tracking"""
    progress_id: str
    plan_id: str
    overall_completion: float
    phase_completion: Dict[IntegrationPhase, float]
    area_completion: Dict[IntegrationArea, float]
    milestones_completed: int
    milestones_total: int
    milestones_at_risk: int
    critical_path_status: str
    estimated_completion_date: Optional[datetime]
    variance_days: int
    budget_variance: float
    key_issues: List[str] = field(default_factory=list)
    recent_achievements: List[str] = field(default_factory=list)
    next_milestones: List[str] = field(default_factory=list)

class IntegrationPlanner:
    """AI-powered integration planning engine"""

    def __init__(self):
        self.integration_templates = {}
        self.milestone_templates = defaultdict(list)
        self.best_practices = defaultdict(list)
        self.industry_benchmarks = {}

    def create_integration_plan(self, deal_id: str, integration_config: Dict[str, Any]) -> str:
        """Create comprehensive integration plan"""

        plan_id = f"integration_{deal_id}_{int(datetime.now().timestamp())}"

        # Determine integration type based on deal characteristics
        integration_type = self._determine_integration_type(integration_config)

        # Generate milestone timeline
        milestones = self._generate_milestone_timeline(integration_config, integration_type)

        # Calculate resource requirements
        resource_requirements = self._calculate_resource_requirements(milestones, integration_config)

        # Set budget allocation
        budget_allocation = self._allocate_budget(integration_config, integration_type)

        # Define success metrics
        success_metrics = self._define_success_metrics(integration_config)

        # Calculate planned completion date
        planned_completion = self._calculate_completion_date(milestones)

        integration_plan = IntegrationPlan(
            plan_id=plan_id,
            deal_id=deal_id,
            integration_type=integration_type,
            target_company=integration_config.get("target_company", ""),
            acquirer_company=integration_config.get("acquirer_company", ""),
            planned_completion_date=planned_completion,
            milestones=milestones,
            success_metrics=success_metrics,
            budget_allocation=budget_allocation,
            resource_requirements=resource_requirements
        )

        return plan_id

    def optimize_integration_timeline(self, plan_id: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize integration timeline using AI algorithms"""

        # Simulate optimization algorithm
        optimization_result = {
            "original_duration_days": 365,
            "optimized_duration_days": 320,
            "time_savings_days": 45,
            "optimization_areas": [
                {
                    "area": "Technology Integration",
                    "original_duration": 180,
                    "optimized_duration": 150,
                    "optimization_method": "Parallel processing and automation"
                },
                {
                    "area": "Operations Integration",
                    "original_duration": 240,
                    "optimized_duration": 210,
                    "optimization_method": "Phased rollout with early wins"
                }
            ],
            "critical_path": [
                "System architecture alignment",
                "Data migration and validation",
                "Process standardization",
                "Team integration",
                "Customer communication"
            ],
            "risk_mitigation": [
                "Implement parallel testing environments",
                "Establish rollback procedures",
                "Create communication protocols",
                "Set up monitoring dashboards"
            ],
            "resource_optimization": {
                "technology_team": {"original": 25, "optimized": 20},
                "operations_team": {"original": 30, "optimized": 28},
                "project_management": {"original": 10, "optimized": 12}
            }
        }

        return optimization_result

    def _determine_integration_type(self, config: Dict[str, Any]) -> IntegrationType:
        """Determine optimal integration type based on deal characteristics"""

        deal_size = config.get("deal_value", 0)
        industry_similarity = config.get("industry_similarity", 0.5)
        cultural_similarity = config.get("cultural_similarity", 0.5)
        technology_compatibility = config.get("technology_compatibility", 0.5)

        # AI decision logic for integration type
        integration_score = (
            industry_similarity * 0.3 +
            cultural_similarity * 0.25 +
            technology_compatibility * 0.25 +
            (1.0 if deal_size > 1_000_000_000 else 0.5) * 0.2
        )

        if integration_score >= 0.8:
            return IntegrationType.FULL_INTEGRATION
        elif integration_score >= 0.6:
            return IntegrationType.HYBRID_MODEL
        elif integration_score >= 0.4:
            return IntegrationType.PARTIAL_INTEGRATION
        else:
            return IntegrationType.STANDALONE_OPERATION

    def _generate_milestone_timeline(self, config: Dict[str, Any],
                                   integration_type: IntegrationType) -> List[IntegrationMilestone]:
        """Generate AI-optimized milestone timeline"""

        milestones = []
        base_start_date = datetime.now()

        # Integration area priorities based on type
        area_priorities = self._get_area_priorities(integration_type)

        # Generate milestones for each integration area
        for area, priority in area_priorities.items():
            area_milestones = self._generate_area_milestones(
                area, priority, base_start_date, config
            )
            milestones.extend(area_milestones)

        # Optimize dependencies and sequencing
        milestones = self._optimize_milestone_sequence(milestones)

        return milestones

    def _get_area_priorities(self, integration_type: IntegrationType) -> Dict[IntegrationArea, int]:
        """Get integration area priorities based on integration type"""

        priority_maps = {
            IntegrationType.FULL_INTEGRATION: {
                IntegrationArea.TECHNOLOGY: 1,
                IntegrationArea.OPERATIONS: 2,
                IntegrationArea.HUMAN_RESOURCES: 3,
                IntegrationArea.FINANCE: 4,
                IntegrationArea.SALES_MARKETING: 5,
                IntegrationArea.LEGAL_COMPLIANCE: 6,
                IntegrationArea.SUPPLY_CHAIN: 7,
                IntegrationArea.CUSTOMER_SERVICE: 8
            },
            IntegrationType.PARTIAL_INTEGRATION: {
                IntegrationArea.TECHNOLOGY: 1,
                IntegrationArea.FINANCE: 2,
                IntegrationArea.LEGAL_COMPLIANCE: 3,
                IntegrationArea.OPERATIONS: 4,
                IntegrationArea.HUMAN_RESOURCES: 5
            },
            IntegrationType.STANDALONE_OPERATION: {
                IntegrationArea.LEGAL_COMPLIANCE: 1,
                IntegrationArea.FINANCE: 2,
                IntegrationArea.TECHNOLOGY: 3
            }
        }

        return priority_maps.get(integration_type, {})

    def _generate_area_milestones(self, area: IntegrationArea, priority: int,
                                start_date: datetime, config: Dict[str, Any]) -> List[IntegrationMilestone]:
        """Generate milestones for specific integration area"""

        milestone_templates = {
            IntegrationArea.TECHNOLOGY: [
                {
                    "name": "IT Infrastructure Assessment",
                    "description": "Complete assessment of both companies' IT infrastructure",
                    "phase": IntegrationPhase.PLANNING,
                    "duration_days": 14,
                    "dependencies": [],
                    "success_criteria": ["Infrastructure mapping completed", "Gap analysis documented"]
                },
                {
                    "name": "System Architecture Design",
                    "description": "Design integrated system architecture",
                    "phase": IntegrationPhase.PLANNING,
                    "duration_days": 21,
                    "dependencies": ["IT Infrastructure Assessment"],
                    "success_criteria": ["Architecture blueprint approved", "Migration plan created"]
                },
                {
                    "name": "Data Migration Planning",
                    "description": "Plan and prepare data migration strategy",
                    "phase": IntegrationPhase.DAY_ONE_READINESS,
                    "duration_days": 30,
                    "dependencies": ["System Architecture Design"],
                    "success_criteria": ["Migration scripts tested", "Data validation rules defined"]
                }
            ],
            IntegrationArea.HUMAN_RESOURCES: [
                {
                    "name": "Organizational Structure Design",
                    "description": "Design integrated organizational structure",
                    "phase": IntegrationPhase.PLANNING,
                    "duration_days": 21,
                    "dependencies": [],
                    "success_criteria": ["Org chart approved", "Role definitions completed"]
                },
                {
                    "name": "Employee Communication Plan",
                    "description": "Develop comprehensive employee communication strategy",
                    "phase": IntegrationPhase.DAY_ONE_READINESS,
                    "duration_days": 14,
                    "dependencies": ["Organizational Structure Design"],
                    "success_criteria": ["Communication plan approved", "FAQ document created"]
                }
            ]
        }

        area_templates = milestone_templates.get(area, [])
        milestones = []

        current_date = start_date + timedelta(days=priority * 7)  # Stagger by priority

        for template in area_templates:
            milestone_id = f"{area.value}_{template['name'].replace(' ', '_').lower()}_{uuid.uuid4().hex[:8]}"

            milestone = IntegrationMilestone(
                milestone_id=milestone_id,
                name=template["name"],
                description=template["description"],
                integration_area=area,
                phase=template["phase"],
                planned_start_date=current_date,
                planned_end_date=current_date + timedelta(days=template["duration_days"]),
                dependencies=template["dependencies"],
                success_criteria=template["success_criteria"],
                risk_level=RiskLevel.MEDIUM
            )

            milestones.append(milestone)
            current_date = milestone.planned_end_date + timedelta(days=1)

        return milestones

    def _optimize_milestone_sequence(self, milestones: List[IntegrationMilestone]) -> List[IntegrationMilestone]:
        """Optimize milestone sequence using dependency analysis"""

        # Create dependency graph
        dependency_graph = {}
        for milestone in milestones:
            dependency_graph[milestone.milestone_id] = milestone.dependencies

        # Topological sort for optimal sequencing
        sorted_milestones = []
        remaining_milestones = milestones.copy()

        while remaining_milestones:
            # Find milestones with no unmet dependencies
            ready_milestones = []
            for milestone in remaining_milestones:
                unmet_deps = [dep for dep in milestone.dependencies
                            if dep not in [m.milestone_id for m in sorted_milestones]]
                if not unmet_deps:
                    ready_milestones.append(milestone)

            if not ready_milestones:
                # Break circular dependencies or add remaining
                ready_milestones = remaining_milestones

            # Sort by phase and priority
            ready_milestones.sort(key=lambda x: (x.phase.value, x.integration_area.value))

            # Add to sorted list
            for milestone in ready_milestones:
                sorted_milestones.append(milestone)
                remaining_milestones.remove(milestone)

        return sorted_milestones

    def _calculate_resource_requirements(self, milestones: List[IntegrationMilestone],
                                       config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate resource requirements for integration"""

        # Count milestones by area
        area_counts = defaultdict(int)
        for milestone in milestones:
            area_counts[milestone.integration_area] += 1

        # Base resource requirements
        resource_requirements = {
            "project_management": {
                "integration_manager": 1,
                "project_coordinators": max(2, len(area_counts) // 3),
                "change_management_specialists": 2
            },
            "technical_resources": {
                "solution_architects": 2,
                "integration_developers": area_counts.get(IntegrationArea.TECHNOLOGY, 0) * 2,
                "data_analysts": 3,
                "qa_engineers": 4
            },
            "business_resources": {
                "business_analysts": len(area_counts),
                "process_improvement_specialists": 2,
                "training_coordinators": area_counts.get(IntegrationArea.HUMAN_RESOURCES, 0),
                "communication_specialists": 2
            },
            "external_consultants": {
                "integration_consultants": 1 if config.get("deal_value", 0) > 500_000_000 else 0,
                "change_management_consultants": 1,
                "technology_consultants": 1 if area_counts.get(IntegrationArea.TECHNOLOGY, 0) > 5 else 0
            }
        }

        return resource_requirements

    def _allocate_budget(self, config: Dict[str, Any],
                        integration_type: IntegrationType) -> Dict[str, float]:
        """Allocate integration budget across areas"""

        deal_value = config.get("deal_value", 0)
        base_budget = deal_value * 0.02  # 2% of deal value for integration

        # Budget allocation percentages by integration type
        allocation_maps = {
            IntegrationType.FULL_INTEGRATION: {
                "technology": 0.35,
                "operations": 0.20,
                "human_resources": 0.15,
                "change_management": 0.10,
                "project_management": 0.10,
                "contingency": 0.10
            },
            IntegrationType.PARTIAL_INTEGRATION: {
                "technology": 0.40,
                "operations": 0.15,
                "human_resources": 0.10,
                "change_management": 0.10,
                "project_management": 0.15,
                "contingency": 0.10
            },
            IntegrationType.STANDALONE_OPERATION: {
                "technology": 0.25,
                "legal_compliance": 0.25,
                "finance": 0.20,
                "project_management": 0.20,
                "contingency": 0.10
            }
        }

        allocation_percentages = allocation_maps.get(integration_type, allocation_maps[IntegrationType.FULL_INTEGRATION])

        budget_allocation = {}
        for area, percentage in allocation_percentages.items():
            budget_allocation[area] = base_budget * percentage

        return budget_allocation

    def _define_success_metrics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Define success metrics for integration"""

        return {
            "timeline_metrics": {
                "planned_completion_variance": {"target": 0, "tolerance": 30},  # days
                "milestone_on_time_delivery": {"target": 0.9, "tolerance": 0.1}
            },
            "financial_metrics": {
                "budget_variance": {"target": 0, "tolerance": 0.1},  # 10%
                "synergy_realization": {"target": 0.8, "tolerance": 0.1}  # 80%
            },
            "operational_metrics": {
                "system_uptime": {"target": 0.99, "tolerance": 0.01},
                "employee_retention": {"target": 0.85, "tolerance": 0.05},
                "customer_satisfaction": {"target": 0.9, "tolerance": 0.05}
            },
            "quality_metrics": {
                "defect_rate": {"target": 0.02, "tolerance": 0.01},
                "rework_percentage": {"target": 0.05, "tolerance": 0.02}
            }
        }

    def _calculate_completion_date(self, milestones: List[IntegrationMilestone]) -> datetime:
        """Calculate overall integration completion date"""

        if not milestones:
            return datetime.now() + timedelta(days=365)

        latest_end_date = max(
            milestone.planned_end_date or datetime.now()
            for milestone in milestones
        )

        # Add buffer for stabilization
        return latest_end_date + timedelta(days=30)

class MilestoneTracker:
    """Real-time milestone tracking and progress monitoring"""

    def __init__(self):
        self.milestone_progress = {}
        self.progress_history = defaultdict(list)
        self.risk_alerts = defaultdict(list)
        self.performance_metrics = defaultdict(dict)

    def update_milestone_progress(self, milestone_id: str, progress_data: Dict[str, Any]) -> bool:
        """Update milestone progress and status"""

        try:
            # Update progress data
            self.milestone_progress[milestone_id] = {
                **self.milestone_progress.get(milestone_id, {}),
                **progress_data,
                "last_updated": datetime.now()
            }

            # Record progress history
            self.progress_history[milestone_id].append({
                "timestamp": datetime.now(),
                "progress_data": progress_data
            })

            # Analyze risks and generate alerts
            self._analyze_milestone_risks(milestone_id, progress_data)

            return True

        except Exception:
            return False

    def calculate_integration_progress(self, plan_id: str, milestones: List[IntegrationMilestone]) -> IntegrationProgress:
        """Calculate comprehensive integration progress"""

        # Overall completion calculation
        total_milestones = len(milestones)
        completed_milestones = sum(1 for m in milestones if m.status == MilestoneStatus.COMPLETED)

        overall_completion = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0

        # Phase completion calculation
        phase_completion = {}
        for phase in IntegrationPhase:
            phase_milestones = [m for m in milestones if m.phase == phase]
            if phase_milestones:
                phase_completed = sum(1 for m in phase_milestones if m.status == MilestoneStatus.COMPLETED)
                phase_completion[phase] = (phase_completed / len(phase_milestones) * 100)
            else:
                phase_completion[phase] = 0.0

        # Area completion calculation
        area_completion = {}
        for area in IntegrationArea:
            area_milestones = [m for m in milestones if m.integration_area == area]
            if area_milestones:
                area_completed = sum(1 for m in area_milestones if m.status == MilestoneStatus.COMPLETED)
                area_completion[area] = (area_completed / len(area_milestones) * 100)
            else:
                area_completion[area] = 0.0

        # Risk analysis
        milestones_at_risk = sum(1 for m in milestones if m.status in [MilestoneStatus.AT_RISK, MilestoneStatus.DELAYED])

        # Critical path analysis
        critical_path_status = self._analyze_critical_path(milestones)

        # Estimated completion date
        estimated_completion = self._estimate_completion_date(milestones)

        # Calculate variance
        planned_completion = max(m.planned_end_date for m in milestones if m.planned_end_date)
        variance_days = (estimated_completion - planned_completion).days if estimated_completion and planned_completion else 0

        # Generate key issues and achievements
        key_issues = self._identify_key_issues(milestones)
        recent_achievements = self._get_recent_achievements(milestones)
        next_milestones = self._get_next_milestones(milestones)

        progress_id = f"progress_{plan_id}_{int(datetime.now().timestamp())}"

        return IntegrationProgress(
            progress_id=progress_id,
            plan_id=plan_id,
            overall_completion=round(overall_completion, 2),
            phase_completion=phase_completion,
            area_completion=area_completion,
            milestones_completed=completed_milestones,
            milestones_total=total_milestones,
            milestones_at_risk=milestones_at_risk,
            critical_path_status=critical_path_status,
            estimated_completion_date=estimated_completion,
            variance_days=variance_days,
            budget_variance=0.0,  # Would be calculated from actual budget tracking
            key_issues=key_issues,
            recent_achievements=recent_achievements,
            next_milestones=next_milestones
        )

    def _analyze_milestone_risks(self, milestone_id: str, progress_data: Dict[str, Any]) -> None:
        """Analyze milestone risks and generate alerts"""

        alerts = []

        # Check completion percentage vs. time elapsed
        completion = progress_data.get("completion_percentage", 0)
        planned_duration = progress_data.get("planned_duration_days", 30)
        elapsed_days = progress_data.get("elapsed_days", 0)

        expected_completion = (elapsed_days / planned_duration) * 100 if planned_duration > 0 else 0

        if completion < expected_completion * 0.8:  # 20% behind schedule
            alerts.append({
                "type": "schedule_risk",
                "severity": "high",
                "message": f"Milestone {milestone_id} is significantly behind schedule"
            })

        # Check for resource constraints
        if progress_data.get("resource_utilization", 0) > 0.9:
            alerts.append({
                "type": "resource_risk",
                "severity": "medium",
                "message": f"High resource utilization detected for milestone {milestone_id}"
            })

        # Check for quality issues
        if progress_data.get("defect_count", 0) > 5:
            alerts.append({
                "type": "quality_risk",
                "severity": "medium",
                "message": f"Quality issues detected in milestone {milestone_id}"
            })

        self.risk_alerts[milestone_id] = alerts

    def _analyze_critical_path(self, milestones: List[IntegrationMilestone]) -> str:
        """Analyze critical path status"""

        critical_milestones = [m for m in milestones if m.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        delayed_critical = [m for m in critical_milestones if m.status == MilestoneStatus.DELAYED]

        if delayed_critical:
            return "CRITICAL_DELAY"
        elif len(critical_milestones) > 0:
            return "AT_RISK"
        else:
            return "ON_TRACK"

    def _estimate_completion_date(self, milestones: List[IntegrationMilestone]) -> Optional[datetime]:
        """Estimate realistic completion date based on current progress"""

        incomplete_milestones = [m for m in milestones if m.status != MilestoneStatus.COMPLETED]

        if not incomplete_milestones:
            return datetime.now()

        # Calculate average velocity
        completed_milestones = [m for m in milestones if m.status == MilestoneStatus.COMPLETED]
        if completed_milestones:
            total_planned_days = sum(
                (m.planned_end_date - m.planned_start_date).days
                for m in completed_milestones if m.planned_end_date and m.planned_start_date
            )
            total_actual_days = sum(
                (m.actual_end_date - m.actual_start_date).days
                for m in completed_milestones if m.actual_end_date and m.actual_start_date
            )

            velocity_factor = total_actual_days / total_planned_days if total_planned_days > 0 else 1.2
        else:
            velocity_factor = 1.2  # Default to 20% longer than planned

        # Estimate remaining work
        remaining_planned_days = sum(
            (m.planned_end_date - m.planned_start_date).days
            for m in incomplete_milestones if m.planned_end_date and m.planned_start_date
        )

        estimated_remaining_days = remaining_planned_days * velocity_factor

        return datetime.now() + timedelta(days=estimated_remaining_days)

    def _identify_key_issues(self, milestones: List[IntegrationMilestone]) -> List[str]:
        """Identify key issues affecting integration"""

        issues = []

        # Delayed milestones
        delayed = [m for m in milestones if m.status == MilestoneStatus.DELAYED]
        if delayed:
            issues.append(f"{len(delayed)} milestones are delayed")

        # Blocked milestones
        blocked = [m for m in milestones if m.status == MilestoneStatus.BLOCKED]
        if blocked:
            issues.append(f"{len(blocked)} milestones are blocked")

        # High-risk milestones
        high_risk = [m for m in milestones if m.risk_level == RiskLevel.HIGH]
        if high_risk:
            issues.append(f"{len(high_risk)} high-risk milestones require attention")

        return issues

    def _get_recent_achievements(self, milestones: List[IntegrationMilestone]) -> List[str]:
        """Get recent achievements and completed milestones"""

        recent_completed = [
            m for m in milestones
            if m.status == MilestoneStatus.COMPLETED and
            m.actual_end_date and
            (datetime.now() - m.actual_end_date).days <= 7
        ]

        achievements = [
            f"Completed: {milestone.name}"
            for milestone in recent_completed[:5]
        ]

        return achievements

    def _get_next_milestones(self, milestones: List[IntegrationMilestone]) -> List[str]:
        """Get next upcoming milestones"""

        upcoming = [
            m for m in milestones
            if m.status == MilestoneStatus.NOT_STARTED and
            m.planned_start_date and
            (m.planned_start_date - datetime.now()).days <= 14
        ]

        # Sort by planned start date
        upcoming.sort(key=lambda x: x.planned_start_date or datetime.now())

        return [f"{milestone.name} (starts {milestone.planned_start_date.strftime('%m/%d')})"
                for milestone in upcoming[:5]]

class IntegrationEngine:
    """Main integration planning and execution engine"""

    def __init__(self):
        self.integration_planner = IntegrationPlanner()
        self.milestone_tracker = MilestoneTracker()
        self.active_integrations = {}
        self.integration_analytics = defaultdict(dict)

    async def initiate_integration(self, deal_id: str, integration_config: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate comprehensive post-merger integration"""

        # Create integration plan
        plan_id = self.integration_planner.create_integration_plan(deal_id, integration_config)

        # Optimize timeline
        optimization_result = self.integration_planner.optimize_integration_timeline(
            plan_id, integration_config.get("constraints", {})
        )

        # Initialize tracking
        self.active_integrations[plan_id] = {
            "deal_id": deal_id,
            "plan_id": plan_id,
            "status": "initiated",
            "start_date": datetime.now(),
            "config": integration_config,
            "optimization": optimization_result
        }

        return {
            "plan_id": plan_id,
            "status": "initiated",
            "optimization_summary": optimization_result,
            "next_steps": [
                "Review and approve integration plan",
                "Assign integration team members",
                "Set up progress tracking dashboards",
                "Begin Day One readiness activities"
            ]
        }

    async def get_integration_dashboard(self, plan_id: str) -> Dict[str, Any]:
        """Get comprehensive integration dashboard"""

        if plan_id not in self.active_integrations:
            raise ValueError(f"Integration plan {plan_id} not found")

        integration_info = self.active_integrations[plan_id]

        # Get sample milestones (would be from actual plan)
        sample_milestones = self._get_sample_milestones()

        # Calculate progress
        progress = self.milestone_tracker.calculate_integration_progress(plan_id, sample_milestones)

        # Calculate analytics
        analytics = self._calculate_integration_analytics(plan_id, sample_milestones)

        dashboard = {
            "plan_id": plan_id,
            "deal_id": integration_info["deal_id"],
            "integration_status": integration_info["status"],
            "progress_summary": progress.__dict__,
            "analytics": analytics,
            "key_metrics": {
                "days_since_start": (datetime.now() - integration_info["start_date"]).days,
                "completion_percentage": progress.overall_completion,
                "milestones_completed": progress.milestones_completed,
                "milestones_at_risk": progress.milestones_at_risk,
                "estimated_days_remaining": progress.variance_days
            },
            "dashboard_timestamp": datetime.now().isoformat()
        }

        return dashboard

    def _get_sample_milestones(self) -> List[IntegrationMilestone]:
        """Get sample milestones for demonstration"""

        milestones = [
            IntegrationMilestone(
                milestone_id="tech_assessment_001",
                name="IT Infrastructure Assessment",
                description="Complete assessment of both companies' IT infrastructure",
                integration_area=IntegrationArea.TECHNOLOGY,
                phase=IntegrationPhase.PLANNING,
                status=MilestoneStatus.COMPLETED,
                planned_start_date=datetime.now() - timedelta(days=30),
                planned_end_date=datetime.now() - timedelta(days=16),
                actual_start_date=datetime.now() - timedelta(days=30),
                actual_end_date=datetime.now() - timedelta(days=14),
                completion_percentage=100.0,
                risk_level=RiskLevel.LOW
            ),
            IntegrationMilestone(
                milestone_id="org_design_001",
                name="Organizational Structure Design",
                description="Design integrated organizational structure",
                integration_area=IntegrationArea.HUMAN_RESOURCES,
                phase=IntegrationPhase.PLANNING,
                status=MilestoneStatus.IN_PROGRESS,
                planned_start_date=datetime.now() - timedelta(days=21),
                planned_end_date=datetime.now() + timedelta(days=7),
                actual_start_date=datetime.now() - timedelta(days=18),
                completion_percentage=75.0,
                risk_level=RiskLevel.MEDIUM
            ),
            IntegrationMilestone(
                milestone_id="data_migration_001",
                name="Data Migration Planning",
                description="Plan and prepare data migration strategy",
                integration_area=IntegrationArea.TECHNOLOGY,
                phase=IntegrationPhase.DAY_ONE_READINESS,
                status=MilestoneStatus.NOT_STARTED,
                planned_start_date=datetime.now() + timedelta(days=7),
                planned_end_date=datetime.now() + timedelta(days=37),
                completion_percentage=0.0,
                risk_level=RiskLevel.HIGH
            )
        ]

        return milestones

    def _calculate_integration_analytics(self, plan_id: str,
                                       milestones: List[IntegrationMilestone]) -> Dict[str, Any]:
        """Calculate comprehensive integration analytics"""

        analytics = {
            "velocity_metrics": {
                "planned_vs_actual_duration": 1.1,  # 10% longer than planned
                "milestone_completion_rate": 0.33,  # 1/3 completed
                "average_completion_time": 16.0  # days
            },
            "risk_metrics": {
                "high_risk_milestones": len([m for m in milestones if m.risk_level == RiskLevel.HIGH]),
                "delayed_milestones": len([m for m in milestones if m.status == MilestoneStatus.DELAYED]),
                "risk_score": 3.2  # out of 10
            },
            "resource_metrics": {
                "team_utilization": 0.85,
                "budget_utilization": 0.23,
                "external_consultant_usage": 0.15
            },
            "quality_metrics": {
                "rework_percentage": 0.08,
                "milestone_success_rate": 0.95,
                "stakeholder_satisfaction": 0.87
            }
        }

        return analytics

# Service instance management
_integration_engine_instance = None

def get_integration_engine() -> IntegrationEngine:
    """Get singleton integration engine instance"""
    global _integration_engine_instance
    if _integration_engine_instance is None:
        _integration_engine_instance = IntegrationEngine()
    return _integration_engine_instance