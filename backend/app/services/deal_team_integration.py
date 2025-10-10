"""
Deal-Team Integration Service
Service for integrating the enhanced team management system with existing deal workflows
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.deal import Deal, DealTeamMember, DealStage, DealActivity
from ..models.teams import (
    Team, TeamMember, TeamTask, TeamType, TeamStatus, TaskStatus,
    TaskPriority, TeamRole
)
from ..models.models import User
from .workflow_management import WorkflowManagementService, TeamFormationEngine

logger = logging.getLogger(__name__)


class DealTeamIntegrationService:
    """Service for integrating teams with deal workflows"""

    def __init__(self, db: Session):
        self.db = db
        self.workflow_service = WorkflowManagementService(db)
        self.team_formation_engine = TeamFormationEngine(db)

    def create_team_for_deal(
        self,
        deal_id: str,
        team_name: Optional[str] = None,
        team_lead_id: Optional[str] = None,
        auto_populate: bool = True
    ) -> Dict[str, Any]:
        """
        Create a dedicated team for a deal

        Args:
            deal_id: Deal ID to create team for
            team_name: Custom team name (optional)
            team_lead_id: Team lead user ID (optional, defaults to deal lead)
            auto_populate: Whether to automatically add existing deal team members

        Returns:
            Created team information and integration details
        """
        try:
            # Get deal information
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise ValueError(f"Deal {deal_id} not found")

            # Generate team name if not provided
            if not team_name:
                team_name = f"{deal.target_company_name} - {deal.deal_type.value.title()} Team"

            # Use deal lead as team lead if not specified
            if not team_lead_id:
                team_lead_id = deal.deal_lead_id

            # Create team
            team_data = {
                "name": team_name,
                "description": f"Deal team for {deal.target_company_name} {deal.deal_type.value}",
                "team_type": TeamType.DEAL_TEAM,
                "team_lead_id": team_lead_id,
                "deal_id": deal_id,
                "organization_id": deal.organization_id,
                "budget_limit": deal.deal_value * Decimal('0.05') if deal.deal_value else None,  # 5% of deal value
                "target_completion_date": deal.expected_close_date
            }

            new_team = self.workflow_service.create_team(team_data)

            # Auto-populate team with existing deal team members
            if auto_populate:
                self._migrate_deal_team_members(deal, new_team)

            # Create initial workflow tasks based on deal stage
            self._create_stage_based_tasks(deal, new_team)

            # Log the integration
            self._log_team_creation_activity(deal, new_team)

            return {
                "team": new_team,
                "deal": deal,
                "members_migrated": auto_populate,
                "initial_tasks_created": True,
                "integration_status": "success"
            }

        except Exception as e:
            logger.error(f"Error creating team for deal {deal_id}: {str(e)}")
            raise

    def sync_deal_team_with_enhanced_team(
        self,
        deal_id: str,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronize existing deal team members with enhanced team structure

        Args:
            deal_id: Deal ID to sync
            team_id: Enhanced team ID (optional, will find or create)

        Returns:
            Synchronization results
        """
        try:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise ValueError(f"Deal {deal_id} not found")

            # Find or create enhanced team
            if team_id:
                team = self.db.query(Team).filter(Team.id == team_id).first()
                if not team:
                    raise ValueError(f"Team {team_id} not found")
            else:
                # Look for existing team linked to this deal
                team = self.db.query(Team).filter(Team.deal_id == deal_id).first()
                if not team:
                    # Create new team
                    result = self.create_team_for_deal(deal_id, auto_populate=False)
                    team = result["team"]

            # Get existing deal team members
            deal_team_members = self.db.query(DealTeamMember).filter(
                DealTeamMember.deal_id == deal_id,
                DealTeamMember.is_active == True
            ).all()

            # Get existing enhanced team members
            existing_team_members = self.db.query(TeamMember).filter(
                TeamMember.team_id == team.id,
                TeamMember.status == "active"
            ).all()

            existing_user_ids = {member.user_id for member in existing_team_members}

            sync_results = {
                "added": 0,
                "updated": 0,
                "skipped": 0,
                "errors": []
            }

            # Sync each deal team member to enhanced team
            for deal_member in deal_team_members:
                try:
                    if deal_member.user_id not in existing_user_ids:
                        # Add new team member
                        team_role = self._map_deal_role_to_team_role(deal_member.role)

                        member_data = {
                            "team_id": team.id,
                            "user_id": deal_member.user_id,
                            "role": team_role,
                            "start_date": deal_member.added_date,
                            "expected_hours_per_week": self._estimate_hours_from_allocation(
                                deal_member.time_allocation_percentage
                            ),
                            "added_by_id": deal.deal_lead_id
                        }

                        self.workflow_service.add_team_member(**member_data)
                        sync_results["added"] += 1
                    else:
                        sync_results["skipped"] += 1

                except Exception as e:
                    logger.error(f"Error syncing deal team member {deal_member.id}: {str(e)}")
                    sync_results["errors"].append(str(e))

            return {
                "deal_id": deal_id,
                "team_id": team.id,
                "sync_results": sync_results,
                "status": "completed"
            }

        except Exception as e:
            logger.error(f"Error syncing deal team {deal_id}: {str(e)}")
            raise

    def create_deal_stage_workflow(
        self,
        deal_id: str,
        team_id: Optional[str] = None,
        workflow_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create workflow tasks based on current deal stage

        Args:
            deal_id: Deal ID
            team_id: Team ID (optional, will find team for deal)
            workflow_template: Workflow template to use (optional)

        Returns:
            Workflow creation results
        """
        try:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise ValueError(f"Deal {deal_id} not found")

            # Find team for deal
            if not team_id:
                team = self.db.query(Team).filter(Team.deal_id == deal_id).first()
                if not team:
                    # Create team first
                    result = self.create_team_for_deal(deal_id)
                    team = result["team"]
            else:
                team = self.db.query(Team).filter(Team.id == team_id).first()
                if not team:
                    raise ValueError(f"Team {team_id} not found")

            # Determine workflow template based on deal stage
            if not workflow_template:
                workflow_template = self._get_workflow_template_for_stage(deal.stage)

            # Create workflow tasks
            tasks = self._create_stage_workflow_tasks(deal, team, workflow_template)

            return {
                "deal_id": deal_id,
                "team_id": team.id,
                "workflow_template": workflow_template,
                "tasks_created": len(tasks),
                "tasks": tasks,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error creating deal stage workflow for {deal_id}: {str(e)}")
            raise

    def update_team_on_deal_stage_change(
        self,
        deal_id: str,
        new_stage: DealStage,
        previous_stage: Optional[DealStage] = None
    ) -> Dict[str, Any]:
        """
        Update team structure and tasks when deal stage changes

        Args:
            deal_id: Deal ID
            new_stage: New deal stage
            previous_stage: Previous deal stage (optional)

        Returns:
            Update results
        """
        try:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise ValueError(f"Deal {deal_id} not found")

            # Find team for deal
            team = self.db.query(Team).filter(Team.deal_id == deal_id).first()
            if not team:
                logger.warning(f"No team found for deal {deal_id}")
                return {"status": "no_team_found"}

            update_results = {
                "stage_transition": f"{previous_stage.value if previous_stage else 'unknown'} -> {new_stage.value}",
                "tasks_created": 0,
                "tasks_updated": 0,
                "team_changes": [],
                "recommendations": []
            }

            # Create new tasks for the new stage
            new_tasks = self._create_stage_workflow_tasks(deal, team, self._get_workflow_template_for_stage(new_stage))
            update_results["tasks_created"] = len(new_tasks)

            # Update task priorities based on new stage
            self._update_task_priorities_for_stage(team.id, new_stage)

            # Get team recommendations for new stage
            recommendations = self._get_team_recommendations_for_stage(deal, team, new_stage)
            update_results["recommendations"] = recommendations

            # Log the stage change activity
            self._log_stage_change_activity(deal, team, new_stage, previous_stage)

            return update_results

        except Exception as e:
            logger.error(f"Error updating team for deal stage change {deal_id}: {str(e)}")
            raise

    def generate_team_recommendations(
        self,
        deal_id: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered team recommendations for a deal

        Args:
            deal_id: Deal ID
            context: Additional context for recommendations

        Returns:
            Team recommendations
        """
        try:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise ValueError(f"Deal {deal_id} not found")

            # Analyze deal requirements
            deal_requirements = self._analyze_deal_requirements(deal)

            # Get current team if exists
            current_team = self.db.query(Team).filter(Team.deal_id == deal_id).first()

            # Generate recommendations using team formation engine
            recommendations = self.team_formation_engine.recommend_team_composition(
                organization_id=deal.organization_id,
                deal_id=deal_id,
                required_skills=deal_requirements["required_skills"],
                team_size=deal_requirements["recommended_team_size"],
                budget_limit=deal.deal_value * Decimal('0.05') if deal.deal_value else None
            )

            # Add deal-specific context
            recommendations["deal_context"] = {
                "deal_stage": deal.stage.value,
                "deal_type": deal.deal_type.value,
                "deal_value": float(deal.deal_value) if deal.deal_value else None,
                "target_industry": deal.target_industry,
                "complexity_score": self._calculate_deal_complexity(deal),
                "timeline_pressure": self._assess_timeline_pressure(deal)
            }

            # Add specific recommendations for current stage
            stage_recommendations = self._get_stage_specific_recommendations(deal, current_team)
            recommendations["stage_specific"] = stage_recommendations

            return recommendations

        except Exception as e:
            logger.error(f"Error generating team recommendations for deal {deal_id}: {str(e)}")
            raise

    def get_team_performance_for_deal(
        self,
        deal_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get team performance metrics for a specific deal

        Args:
            deal_id: Deal ID
            period_days: Analysis period in days

        Returns:
            Performance metrics
        """
        try:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise ValueError(f"Deal {deal_id} not found")

            team = self.db.query(Team).filter(Team.deal_id == deal_id).first()
            if not team:
                return {"status": "no_team_found"}

            # Get team performance metrics
            end_date = date.today()
            start_date = end_date - datetime.timedelta(days=period_days)

            metrics = self.workflow_service.calculate_team_performance_metrics(
                team_id=team.id,
                start_date=start_date,
                end_date=end_date
            )

            # Add deal-specific metrics
            deal_metrics = self._calculate_deal_specific_metrics(deal, team, start_date, end_date)
            metrics.update(deal_metrics)

            return {
                "deal_id": deal_id,
                "team_id": team.id,
                "period": {"start": start_date, "end": end_date},
                "metrics": metrics,
                "deal_progress": self._calculate_deal_progress(deal, team)
            }

        except Exception as e:
            logger.error(f"Error getting team performance for deal {deal_id}: {str(e)}")
            raise

    # Helper methods

    def _migrate_deal_team_members(self, deal: Deal, team: Team) -> None:
        """Migrate existing deal team members to enhanced team structure"""
        deal_team_members = self.db.query(DealTeamMember).filter(
            DealTeamMember.deal_id == deal.id,
            DealTeamMember.is_active == True
        ).all()

        for deal_member in deal_team_members:
            team_role = self._map_deal_role_to_team_role(deal_member.role)

            member_data = {
                "team_id": team.id,
                "user_id": deal_member.user_id,
                "role": team_role,
                "start_date": deal_member.added_date,
                "expected_hours_per_week": self._estimate_hours_from_allocation(
                    deal_member.time_allocation_percentage
                ),
                "added_by_id": deal.deal_lead_id
            }

            try:
                self.workflow_service.add_team_member(**member_data)
            except Exception as e:
                logger.error(f"Error migrating deal team member {deal_member.id}: {str(e)}")

    def _map_deal_role_to_team_role(self, deal_role: str) -> TeamRole:
        """Map deal role to enhanced team role"""
        role_mapping = {
            "Deal Lead": TeamRole.LEAD,
            "Lead": TeamRole.LEAD,
            "Senior Analyst": TeamRole.ADMIN,
            "Analyst": TeamRole.MEMBER,
            "Legal": TeamRole.MEMBER,
            "Financial": TeamRole.MEMBER,
            "Consultant": TeamRole.CONSULTANT,
            "Observer": TeamRole.OBSERVER
        }

        return role_mapping.get(deal_role, TeamRole.MEMBER)

    def _estimate_hours_from_allocation(self, allocation_percentage: Optional[int]) -> Optional[int]:
        """Estimate weekly hours from allocation percentage"""
        if not allocation_percentage:
            return None

        # Assume 40-hour work week
        return int((allocation_percentage / 100) * 40)

    def _create_stage_based_tasks(self, deal: Deal, team: Team) -> List[TeamTask]:
        """Create initial tasks based on deal stage"""
        return self._create_stage_workflow_tasks(deal, team, self._get_workflow_template_for_stage(deal.stage))

    def _get_workflow_template_for_stage(self, stage: DealStage) -> str:
        """Get appropriate workflow template for deal stage"""
        stage_templates = {
            DealStage.SOURCING: "deal_sourcing",
            DealStage.INITIAL_REVIEW: "initial_screening",
            DealStage.NDA_EXECUTION: "nda_workflow",
            DealStage.PRELIMINARY_ANALYSIS: "preliminary_analysis",
            DealStage.VALUATION: "valuation_workflow",
            DealStage.DUE_DILIGENCE: "due_diligence",
            DealStage.NEGOTIATION: "negotiation_workflow",
            DealStage.LOI_DRAFTING: "loi_workflow",
            DealStage.DOCUMENTATION: "documentation_workflow",
            DealStage.CLOSING: "closing_workflow"
        }

        return stage_templates.get(stage, "general_deal_workflow")

    def _create_stage_workflow_tasks(self, deal: Deal, team: Team, template: str) -> List[TeamTask]:
        """Create workflow tasks for a specific stage"""
        # Task templates for different deal stages
        task_templates = {
            "due_diligence": [
                {
                    "title": "Financial Due Diligence",
                    "description": "Review financial statements, projections, and accounting practices",
                    "priority": TaskPriority.HIGH,
                    "estimated_hours": 40,
                    "required_skills": ["Financial Analysis", "Accounting"]
                },
                {
                    "title": "Legal Due Diligence",
                    "description": "Review contracts, legal structure, and compliance",
                    "priority": TaskPriority.HIGH,
                    "estimated_hours": 30,
                    "required_skills": ["Legal", "Contract Review"]
                },
                {
                    "title": "Commercial Due Diligence",
                    "description": "Analyze market position, customers, and competitive landscape",
                    "priority": TaskPriority.MEDIUM,
                    "estimated_hours": 25,
                    "required_skills": ["Market Research", "Industry Analysis"]
                },
                {
                    "title": "Operational Due Diligence",
                    "description": "Review operations, systems, and management",
                    "priority": TaskPriority.MEDIUM,
                    "estimated_hours": 20,
                    "required_skills": ["Operations", "Management Assessment"]
                }
            ],
            "valuation_workflow": [
                {
                    "title": "DCF Model Development",
                    "description": "Build discounted cash flow valuation model",
                    "priority": TaskPriority.HIGH,
                    "estimated_hours": 20,
                    "required_skills": ["Financial Modeling", "Valuation"]
                },
                {
                    "title": "Comparable Company Analysis",
                    "description": "Analyze comparable public companies",
                    "priority": TaskPriority.HIGH,
                    "estimated_hours": 15,
                    "required_skills": ["Valuation", "Market Research"]
                },
                {
                    "title": "Precedent Transaction Analysis",
                    "description": "Review precedent M&A transactions",
                    "priority": TaskPriority.MEDIUM,
                    "estimated_hours": 12,
                    "required_skills": ["Valuation", "Research"]
                }
            ]
        }

        template_tasks = task_templates.get(template, [])
        created_tasks = []

        for task_template in template_tasks:
            task_data = {
                "team_id": team.id,
                "title": task_template["title"],
                "description": task_template["description"],
                "priority": task_template["priority"],
                "estimated_hours": task_template["estimated_hours"],
                "created_by_id": deal.deal_lead_id,
                "due_date": deal.expected_close_date
            }

            try:
                task = self.workflow_service.create_task(task_data)
                created_tasks.append(task)
            except Exception as e:
                logger.error(f"Error creating task from template: {str(e)}")

        return created_tasks

    def _analyze_deal_requirements(self, deal: Deal) -> Dict[str, Any]:
        """Analyze deal to determine team requirements"""
        required_skills = ["Financial Analysis", "Due Diligence"]
        team_size = 5

        # Add skills based on deal type
        if deal.deal_type in [deal.DealType.MERGER, deal.DealType.ACQUISITION]:
            required_skills.extend(["Legal", "Integration Planning"])
            team_size = 6

        # Add skills based on deal value
        if deal.deal_value and deal.deal_value > 100000000:  # > $100M
            required_skills.extend(["Investment Banking", "Tax"])
            team_size = 8

        # Add skills based on industry
        if deal.target_industry:
            required_skills.append(f"{deal.target_industry} Expertise")

        return {
            "required_skills": required_skills,
            "recommended_team_size": team_size,
            "complexity_factors": self._identify_complexity_factors(deal)
        }

    def _calculate_deal_complexity(self, deal: Deal) -> float:
        """Calculate deal complexity score (0-100)"""
        complexity = 50.0  # Base complexity

        # Deal value impact
        if deal.deal_value:
            if deal.deal_value > 1000000000:  # > $1B
                complexity += 20
            elif deal.deal_value > 100000000:  # > $100M
                complexity += 10

        # Deal type impact
        complex_types = [Deal.DealType.MERGER, Deal.DealType.LEVERAGED_BUYOUT]
        if deal.deal_type in complex_types:
            complexity += 15

        # Cross-border impact
        if deal.target_country and deal.target_country != "US":
            complexity += 10

        # Timeline pressure
        if deal.expected_close_date:
            days_to_close = (deal.expected_close_date - date.today()).days
            if days_to_close < 60:
                complexity += 15
            elif days_to_close < 120:
                complexity += 10

        return min(complexity, 100.0)

    def _assess_timeline_pressure(self, deal: Deal) -> str:
        """Assess timeline pressure for deal"""
        if not deal.expected_close_date:
            return "unknown"

        days_to_close = (deal.expected_close_date - date.today()).days

        if days_to_close < 30:
            return "critical"
        elif days_to_close < 60:
            return "high"
        elif days_to_close < 120:
            return "medium"
        else:
            return "low"

    def _identify_complexity_factors(self, deal: Deal) -> List[str]:
        """Identify factors that add complexity to the deal"""
        factors = []

        if deal.deal_value and deal.deal_value > 1000000000:
            factors.append("Large deal value (>$1B)")

        if deal.deal_type in [Deal.DealType.MERGER, Deal.DealType.LEVERAGED_BUYOUT]:
            factors.append("Complex transaction structure")

        if deal.target_country and deal.target_country != "US":
            factors.append("Cross-border transaction")

        if deal.expected_close_date:
            days_to_close = (deal.expected_close_date - date.today()).days
            if days_to_close < 60:
                factors.append("Tight timeline")

        return factors

    def _get_stage_specific_recommendations(self, deal: Deal, team: Optional[Team]) -> List[str]:
        """Get recommendations specific to current deal stage"""
        recommendations = []

        if deal.stage == DealStage.DUE_DILIGENCE:
            recommendations.extend([
                "Ensure dedicated financial analyst for DD workstream",
                "Consider adding industry expert for commercial DD",
                "Schedule regular DD status meetings"
            ])
        elif deal.stage == DealStage.NEGOTIATION:
            recommendations.extend([
                "Include senior legal counsel in negotiations",
                "Add business development lead for deal structuring",
                "Consider external advisor for complex terms"
            ])

        return recommendations

    def _log_team_creation_activity(self, deal: Deal, team: Team) -> None:
        """Log team creation as deal activity"""
        activity = DealActivity(
            deal_id=deal.id,
            organization_id=deal.organization_id,
            activity_type="team_created",
            subject=f"Deal team created: {team.name}",
            description=f"Enhanced deal team '{team.name}' was created for {deal.target_company_name}",
            activity_date=datetime.utcnow()
        )

        self.db.add(activity)
        self.db.commit()

    def _log_stage_change_activity(
        self,
        deal: Deal,
        team: Team,
        new_stage: DealStage,
        previous_stage: Optional[DealStage]
    ) -> None:
        """Log stage change and team updates as deal activity"""
        activity = DealActivity(
            deal_id=deal.id,
            organization_id=deal.organization_id,
            activity_type="stage_change",
            subject=f"Deal stage changed to {new_stage.value}",
            description=f"Deal stage updated from {previous_stage.value if previous_stage else 'unknown'} to {new_stage.value}. Team workflows updated.",
            activity_date=datetime.utcnow()
        )

        self.db.add(activity)
        self.db.commit()

    def _update_task_priorities_for_stage(self, team_id: str, stage: DealStage) -> None:
        """Update task priorities based on new deal stage"""
        # Define priority mappings for different stages
        stage_priorities = {
            DealStage.DUE_DILIGENCE: {
                "Financial Due Diligence": TaskPriority.HIGH,
                "Legal Due Diligence": TaskPriority.HIGH,
                "Commercial Due Diligence": TaskPriority.MEDIUM
            },
            DealStage.NEGOTIATION: {
                "Term Sheet Review": TaskPriority.HIGH,
                "Legal Documentation": TaskPriority.HIGH,
                "Financial Model": TaskPriority.MEDIUM
            }
        }

        priorities = stage_priorities.get(stage, {})

        for task_title, priority in priorities.items():
            tasks = self.db.query(TeamTask).filter(
                TeamTask.team_id == team_id,
                TeamTask.title.ilike(f"%{task_title}%"),
                TeamTask.status != TaskStatus.COMPLETED
            ).all()

            for task in tasks:
                task.priority = priority

        self.db.commit()

    def _get_team_recommendations_for_stage(
        self,
        deal: Deal,
        team: Team,
        stage: DealStage
    ) -> List[str]:
        """Get team recommendations for specific stage"""
        recommendations = []

        current_members = self.db.query(TeamMember).filter(
            TeamMember.team_id == team.id,
            TeamMember.status == "active"
        ).count()

        stage_requirements = {
            DealStage.DUE_DILIGENCE: {
                "min_members": 6,
                "required_roles": ["Financial Analyst", "Legal Counsel"],
                "recommendations": [
                    "Consider adding dedicated DD coordinators",
                    "Ensure industry expertise is available"
                ]
            },
            DealStage.NEGOTIATION: {
                "min_members": 4,
                "required_roles": ["Legal Counsel", "Deal Lead"],
                "recommendations": [
                    "Include senior decision makers",
                    "Consider external legal advisor for complex terms"
                ]
            }
        }

        requirements = stage_requirements.get(stage, {})

        if current_members < requirements.get("min_members", 0):
            recommendations.append(f"Consider adding more team members (current: {current_members}, recommended: {requirements['min_members']})")

        recommendations.extend(requirements.get("recommendations", []))

        return recommendations

    def _calculate_deal_specific_metrics(
        self,
        deal: Deal,
        team: Team,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Calculate deal-specific performance metrics"""
        # Calculate days in current stage
        stage_duration = (datetime.utcnow().date() - deal.created_at.date()).days

        # Calculate deal progress
        progress = self._calculate_deal_progress(deal, team)

        return {
            "deal_stage_duration_days": stage_duration,
            "deal_progress_percentage": progress,
            "days_to_expected_close": deal.days_to_expected_close,
            "is_on_track": not deal.is_overdue,
            "deal_value_per_team_member": float(deal.deal_value or 0) / team.member_count if team.member_count > 0 else 0
        }

    def _calculate_deal_progress(self, deal: Deal, team: Team) -> float:
        """Calculate overall deal progress percentage"""
        # Simple stage-based progress calculation
        stage_progress = {
            DealStage.SOURCING: 5,
            DealStage.INITIAL_REVIEW: 10,
            DealStage.NDA_EXECUTION: 15,
            DealStage.PRELIMINARY_ANALYSIS: 25,
            DealStage.VALUATION: 35,
            DealStage.DUE_DILIGENCE: 50,
            DealStage.NEGOTIATION: 70,
            DealStage.LOI_DRAFTING: 80,
            DealStage.DOCUMENTATION: 90,
            DealStage.CLOSING: 95,
            DealStage.CLOSED_WON: 100,
            DealStage.CLOSED_LOST: 0
        }

        base_progress = stage_progress.get(deal.stage, 0)

        # Adjust based on team task completion
        team_tasks = self.db.query(TeamTask).filter(TeamTask.team_id == team.id).all()
        if team_tasks:
            completed_tasks = [t for t in team_tasks if t.status == TaskStatus.COMPLETED]
            task_completion_rate = len(completed_tasks) / len(team_tasks)

            # Add up to 20% progress based on task completion within current stage
            stage_task_bonus = task_completion_rate * 20
            base_progress = min(base_progress + stage_task_bonus, 100)

        return base_progress


# Export the service
__all__ = ["DealTeamIntegrationService"]