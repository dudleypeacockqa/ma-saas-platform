"""
Integration Management Services
Comprehensive service layer for post-acquisition integration planning and execution
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from app.models.integration import (
    IntegrationProject, IntegrationMilestone, SynergyOpportunity, IntegrationWorkstream,
    IntegrationTask, CulturalAssessment, ChangeInitiative, PerformanceMetric, IntegrationRisk,
    IntegrationDocument, IntegrationApproach, IntegrationStatus, MilestoneType, MilestoneStatus,
    SynergyType, SynergyStatus, WorkstreamType, TaskPriority, TaskStatus, ChangeType,
    RiskLevel, RiskStatus, DocumentType
)
from app.models.deal import Deal

logger = logging.getLogger(__name__)


class IntegrationProjectService:
    """Service for managing integration projects and overall orchestration"""

    def __init__(self, db: Session):
        self.db = db

    def create_integration_project(
        self,
        organization_id: str,
        deal_id: str,
        project_data: Dict[str, Any]
    ) -> IntegrationProject:
        """Create a new integration project from a closed deal"""

        # Verify deal exists and is closed
        deal = self.db.query(Deal).filter(
            and_(
                Deal.id == deal_id,
                Deal.organization_id == organization_id
            )
        ).first()

        if not deal:
            raise ValueError("Deal not found")

        # Check if integration project already exists
        existing_project = self.db.query(IntegrationProject).filter(
            and_(
                IntegrationProject.organization_id == organization_id,
                IntegrationProject.deal_id == deal_id,
                IntegrationProject.deleted_at.is_(None)
            )
        ).first()

        if existing_project:
            raise ValueError("Integration project already exists for this deal")

        # Create project
        project = IntegrationProject(
            organization_id=organization_id,
            deal_id=deal_id,
            project_name=project_data.get("project_name", f"{deal.company_name} Integration"),
            project_code=project_data.get("project_code"),
            integration_approach=project_data.get("integration_approach", IntegrationApproach.SYMBIOSIS),
            status=IntegrationStatus.PLANNING,
            start_date=project_data.get("start_date", datetime.utcnow()),
            target_completion_date=project_data.get("target_completion_date"),
            integration_lead_user_id=project_data.get("integration_lead_user_id"),
            steering_committee=project_data.get("steering_committee", []),
            target_synergies=project_data.get("target_synergies"),
            integration_budget=project_data.get("integration_budget"),
            executive_summary=project_data.get("executive_summary")
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        logger.info(f"Created integration project {project.id} for deal {deal_id}")

        # Create default milestones
        self._create_default_milestones(project.id, organization_id, project.start_date)

        # Create default workstreams
        self._create_default_workstreams(project.id, organization_id)

        return project

    def _create_default_milestones(
        self,
        project_id: str,
        organization_id: str,
        start_date: datetime
    ):
        """Create default integration milestones"""

        default_milestones = [
            {
                "name": "Pre-Closing Planning",
                "type": MilestoneType.PRE_CLOSING,
                "days_from_start": -30,
                "deliverables": [
                    "Integration strategy document",
                    "Day 1 plan finalized",
                    "Communication materials prepared",
                    "IT infrastructure assessment"
                ]
            },
            {
                "name": "Day 1 Readiness",
                "type": MilestoneType.DAY_1,
                "days_from_start": 0,
                "deliverables": [
                    "Welcome communications sent",
                    "Access and systems provisioned",
                    "Leadership announcements made",
                    "Employee Q&A sessions scheduled"
                ]
            },
            {
                "name": "30-Day Integration Checkpoint",
                "type": MilestoneType.DAY_30,
                "days_from_start": 30,
                "deliverables": [
                    "Quick wins identified and executed",
                    "Key personnel retention confirmed",
                    "Customer communications completed",
                    "Integration health check review"
                ]
            },
            {
                "name": "100-Day Integration Review",
                "type": MilestoneType.DAY_100,
                "days_from_start": 100,
                "deliverables": [
                    "Major system integrations completed",
                    "Synergy tracking established",
                    "Cultural integration progress assessed",
                    "Performance metrics reviewed"
                ]
            },
            {
                "name": "Year 1 Integration Completion",
                "type": MilestoneType.YEAR_1,
                "days_from_start": 365,
                "deliverables": [
                    "All workstreams completed",
                    "Synergy targets achieved",
                    "Full operational integration",
                    "Lessons learned documented"
                ]
            }
        ]

        for milestone_data in default_milestones:
            target_date = start_date + timedelta(days=milestone_data["days_from_start"])

            milestone = IntegrationMilestone(
                organization_id=organization_id,
                project_id=project_id,
                milestone_name=milestone_data["name"],
                milestone_type=milestone_data["type"],
                target_date=target_date,
                key_deliverables=milestone_data["deliverables"],
                success_criteria=[],
                status=MilestoneStatus.NOT_STARTED
            )
            self.db.add(milestone)

        self.db.commit()

    def _create_default_workstreams(
        self,
        project_id: str,
        organization_id: str
    ):
        """Create default integration workstreams"""

        default_workstreams = [
            {
                "name": "IT Systems Integration",
                "type": WorkstreamType.IT_SYSTEMS,
                "objectives": [
                    "Integrate core business systems",
                    "Migrate data and applications",
                    "Establish unified IT infrastructure",
                    "Ensure cybersecurity compliance"
                ]
            },
            {
                "name": "HR & Organization",
                "type": WorkstreamType.HR_ORGANIZATION,
                "objectives": [
                    "Harmonize compensation and benefits",
                    "Integrate HR systems and processes",
                    "Manage organizational structure changes",
                    "Support talent retention and development"
                ]
            },
            {
                "name": "Finance & Accounting",
                "type": WorkstreamType.FINANCE_ACCOUNTING,
                "objectives": [
                    "Integrate financial systems",
                    "Consolidate reporting and controls",
                    "Align budgeting and planning processes",
                    "Achieve synergy targets"
                ]
            },
            {
                "name": "Operations Integration",
                "type": WorkstreamType.OPERATIONS,
                "objectives": [
                    "Streamline operational processes",
                    "Optimize supply chain and logistics",
                    "Integrate facilities and assets",
                    "Improve operational efficiency"
                ]
            },
            {
                "name": "Sales & Marketing",
                "type": WorkstreamType.SALES_MARKETING,
                "objectives": [
                    "Align go-to-market strategies",
                    "Integrate CRM and sales systems",
                    "Unify brand and marketing",
                    "Cross-sell and upsell opportunities"
                ]
            },
            {
                "name": "Customer Integration",
                "type": WorkstreamType.CUSTOMER_INTEGRATION,
                "objectives": [
                    "Communicate changes to customers",
                    "Ensure service continuity",
                    "Migrate customer accounts",
                    "Identify cross-sell opportunities"
                ]
            }
        ]

        for workstream_data in default_workstreams:
            workstream = IntegrationWorkstream(
                organization_id=organization_id,
                project_id=project_id,
                workstream_name=workstream_data["name"],
                workstream_type=workstream_data["type"],
                objectives=workstream_data["objectives"],
                key_deliverables=[],
                status=IntegrationStatus.PLANNING,
                health_status="green"
            )
            self.db.add(workstream)

        self.db.commit()

    def get_project_dashboard(
        self,
        project_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive project dashboard data"""

        project = self.db.query(IntegrationProject).filter(
            and_(
                IntegrationProject.id == project_id,
                IntegrationProject.organization_id == organization_id,
                IntegrationProject.deleted_at.is_(None)
            )
        ).first()

        if not project:
            raise ValueError("Project not found")

        # Get milestone summary
        milestones = self.db.query(IntegrationMilestone).filter(
            and_(
                IntegrationMilestone.project_id == project_id,
                IntegrationMilestone.deleted_at.is_(None)
            )
        ).all()

        milestone_summary = {
            "total": len(milestones),
            "completed": sum(1 for m in milestones if m.status == MilestoneStatus.COMPLETED),
            "in_progress": sum(1 for m in milestones if m.status == MilestoneStatus.IN_PROGRESS),
            "at_risk": sum(1 for m in milestones if m.status == MilestoneStatus.AT_RISK),
            "delayed": sum(1 for m in milestones if m.status == MilestoneStatus.DELAYED)
        }

        # Get synergy summary
        synergies = self.db.query(SynergyOpportunity).filter(
            and_(
                SynergyOpportunity.project_id == project_id,
                SynergyOpportunity.deleted_at.is_(None)
            )
        ).all()

        synergy_summary = {
            "target_total": float(sum(s.target_value or 0 for s in synergies)),
            "realized_total": float(sum(s.realized_value or 0 for s in synergies)),
            "by_type": self._summarize_synergies_by_type(synergies),
            "realization_rate": self._calculate_realization_rate(synergies)
        }

        # Get workstream summary
        workstreams = self.db.query(IntegrationWorkstream).filter(
            and_(
                IntegrationWorkstream.project_id == project_id,
                IntegrationWorkstream.deleted_at.is_(None)
            )
        ).all()

        workstream_summary = {
            "total": len(workstreams),
            "health_status": {
                "green": sum(1 for w in workstreams if w.health_status == "green"),
                "amber": sum(1 for w in workstreams if w.health_status == "amber"),
                "red": sum(1 for w in workstreams if w.health_status == "red")
            },
            "avg_completion": sum(w.completion_percent or 0 for w in workstreams) / len(workstreams) if workstreams else 0
        }

        # Get risk summary
        risks = self.db.query(IntegrationRisk).filter(
            and_(
                IntegrationRisk.project_id == project_id,
                IntegrationRisk.is_active == True,
                IntegrationRisk.deleted_at.is_(None)
            )
        ).all()

        risk_summary = {
            "total_active": len(risks),
            "by_level": {
                "critical": sum(1 for r in risks if r.risk_level == RiskLevel.CRITICAL),
                "high": sum(1 for r in risks if r.risk_level == RiskLevel.HIGH),
                "medium": sum(1 for r in risks if r.risk_level == RiskLevel.MEDIUM),
                "low": sum(1 for r in risks if r.risk_level == RiskLevel.LOW)
            }
        }

        return {
            "project": {
                "id": project.id,
                "name": project.project_name,
                "status": project.status.value,
                "progress_percent": project.overall_progress_percent,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "target_completion": project.target_completion_date.isoformat() if project.target_completion_date else None,
                "health_score": project.overall_health_score
            },
            "milestones": milestone_summary,
            "synergies": synergy_summary,
            "workstreams": workstream_summary,
            "risks": risk_summary,
            "budget": {
                "allocated": float(project.integration_budget or 0),
                "spent": float(project.actual_integration_cost or 0),
                "remaining": float((project.integration_budget or 0) - (project.actual_integration_cost or 0))
            }
        }

    def _summarize_synergies_by_type(self, synergies: List[SynergyOpportunity]) -> Dict[str, Dict[str, float]]:
        """Summarize synergies by type"""
        by_type = {}
        for synergy_type in SynergyType:
            type_synergies = [s for s in synergies if s.synergy_type == synergy_type]
            by_type[synergy_type.value] = {
                "target": float(sum(s.target_value or 0 for s in type_synergies)),
                "realized": float(sum(s.realized_value or 0 for s in type_synergies)),
                "count": len(type_synergies)
            }
        return by_type

    def _calculate_realization_rate(self, synergies: List[SynergyOpportunity]) -> float:
        """Calculate overall synergy realization rate"""
        total_target = sum(s.target_value or 0 for s in synergies)
        total_realized = sum(s.realized_value or 0 for s in synergies)

        if total_target == 0:
            return 0.0

        return round(float(total_realized / total_target * 100), 2)

    def update_project_health(
        self,
        project_id: str,
        organization_id: str
    ) -> int:
        """Calculate and update project health score (0-100)"""

        project = self.db.query(IntegrationProject).filter(
            and_(
                IntegrationProject.id == project_id,
                IntegrationProject.organization_id == organization_id,
                IntegrationProject.deleted_at.is_(None)
            )
        ).first()

        if not project:
            raise ValueError("Project not found")

        # Calculate health score based on multiple factors
        scores = []

        # 1. Milestone completion (25%)
        milestones = self.db.query(IntegrationMilestone).filter(
            and_(
                IntegrationMilestone.project_id == project_id,
                IntegrationMilestone.deleted_at.is_(None)
            )
        ).all()

        if milestones:
            milestone_score = sum(m.completion_percent or 0 for m in milestones) / len(milestones)
            # Penalize for at-risk or delayed milestones
            at_risk_penalty = sum(20 for m in milestones if m.status in [MilestoneStatus.AT_RISK, MilestoneStatus.DELAYED])
            milestone_score = max(0, milestone_score - at_risk_penalty)
            scores.append(milestone_score * 0.25)

        # 2. Synergy realization (25%)
        synergies = self.db.query(SynergyOpportunity).filter(
            and_(
                SynergyOpportunity.project_id == project_id,
                SynergyOpportunity.deleted_at.is_(None)
            )
        ).all()

        if synergies:
            realization_rate = self._calculate_realization_rate(synergies)
            scores.append(realization_rate * 0.25)

        # 3. Workstream health (25%)
        workstreams = self.db.query(IntegrationWorkstream).filter(
            and_(
                IntegrationWorkstream.project_id == project_id,
                IntegrationWorkstream.deleted_at.is_(None)
            )
        ).all()

        if workstreams:
            health_scores = {
                "green": 100,
                "amber": 60,
                "red": 20
            }
            avg_health = sum(health_scores.get(w.health_status, 0) for w in workstreams) / len(workstreams)
            scores.append(avg_health * 0.25)

        # 4. Risk profile (25%)
        active_risks = self.db.query(IntegrationRisk).filter(
            and_(
                IntegrationRisk.project_id == project_id,
                IntegrationRisk.is_active == True,
                IntegrationRisk.deleted_at.is_(None)
            )
        ).all()

        # Lower score if more high-severity risks
        risk_penalties = {
            RiskLevel.CRITICAL: 30,
            RiskLevel.HIGH: 15,
            RiskLevel.MEDIUM: 5,
            RiskLevel.LOW: 0
        }
        total_risk_penalty = sum(risk_penalties.get(r.risk_level, 0) for r in active_risks)
        risk_score = max(0, 100 - total_risk_penalty)
        scores.append(risk_score * 0.25)

        # Calculate overall health score
        overall_health = int(sum(scores))

        # Update project
        project.overall_health_score = overall_health
        self.db.commit()

        logger.info(f"Updated project {project_id} health score to {overall_health}")

        return overall_health


class SynergyTrackingService:
    """Service for tracking and managing synergy opportunities"""

    def __init__(self, db: Session):
        self.db = db

    def create_synergy(
        self,
        organization_id: str,
        project_id: str,
        synergy_data: Dict[str, Any]
    ) -> SynergyOpportunity:
        """Create a new synergy opportunity"""

        synergy = SynergyOpportunity(
            organization_id=organization_id,
            project_id=project_id,
            synergy_name=synergy_data["synergy_name"],
            synergy_type=synergy_data["synergy_type"],
            description=synergy_data.get("description"),
            target_value=synergy_data["target_value"],
            currency=synergy_data.get("currency", "USD"),
            target_realization_date=synergy_data["target_realization_date"],
            realization_period_months=synergy_data.get("realization_period_months"),
            status=SynergyStatus.IDENTIFIED,
            confidence_level=synergy_data.get("confidence_level", 50),
            implementation_plan=synergy_data.get("implementation_plan"),
            owner_user_id=synergy_data.get("owner_user_id"),
            responsible_team=synergy_data.get("responsible_team")
        )

        self.db.add(synergy)
        self.db.commit()
        self.db.refresh(synergy)

        logger.info(f"Created synergy {synergy.id} for project {project_id}")

        return synergy

    def update_synergy_realization(
        self,
        synergy_id: str,
        organization_id: str,
        realized_value: Decimal,
        notes: Optional[str] = None
    ) -> SynergyOpportunity:
        """Update synergy realization value"""

        synergy = self.db.query(SynergyOpportunity).filter(
            and_(
                SynergyOpportunity.id == synergy_id,
                SynergyOpportunity.organization_id == organization_id,
                SynergyOpportunity.deleted_at.is_(None)
            )
        ).first()

        if not synergy:
            raise ValueError("Synergy not found")

        # Update realized value
        synergy.realized_value = realized_value

        # Update status based on realization
        realization_rate = float(realized_value / synergy.target_value * 100) if synergy.target_value > 0 else 0

        if realization_rate >= 100:
            synergy.status = SynergyStatus.REALIZED
            synergy.actual_realization_date = datetime.utcnow()
        elif realization_rate > 0:
            synergy.status = SynergyStatus.IN_PROGRESS

        # Add to monthly tracking
        current_month = datetime.utcnow().strftime("%Y-%m")
        monthly_tracking = synergy.monthly_tracking or {}
        monthly_tracking[current_month] = float(realized_value)
        synergy.monthly_tracking = monthly_tracking

        if notes:
            synergy.notes = notes

        self.db.commit()
        self.db.refresh(synergy)

        # Update project's realized synergies total
        self._update_project_synergies(synergy.project_id)

        return synergy

    def _update_project_synergies(self, project_id: str):
        """Update project's total realized synergies"""

        project = self.db.query(IntegrationProject).filter(
            IntegrationProject.id == project_id
        ).first()

        if not project:
            return

        synergies = self.db.query(SynergyOpportunity).filter(
            and_(
                SynergyOpportunity.project_id == project_id,
                SynergyOpportunity.deleted_at.is_(None)
            )
        ).all()

        total_realized = sum(s.realized_value or 0 for s in synergies)
        project.realized_synergies = total_realized

        self.db.commit()

    def get_synergy_trends(
        self,
        project_id: str,
        organization_id: str,
        months: int = 12
    ) -> Dict[str, Any]:
        """Get synergy realization trends over time"""

        synergies = self.db.query(SynergyOpportunity).filter(
            and_(
                SynergyOpportunity.project_id == project_id,
                SynergyOpportunity.organization_id == organization_id,
                SynergyOpportunity.deleted_at.is_(None)
            )
        ).all()

        # Aggregate monthly data
        monthly_totals = {}

        for synergy in synergies:
            if synergy.monthly_tracking:
                for month, value in synergy.monthly_tracking.items():
                    monthly_totals[month] = monthly_totals.get(month, 0) + value

        # Sort by month
        sorted_months = sorted(monthly_totals.keys())[-months:]

        return {
            "months": sorted_months,
            "values": [monthly_totals[m] for m in sorted_months],
            "by_type": self._get_trends_by_type(synergies, sorted_months)
        }

    def _get_trends_by_type(
        self,
        synergies: List[SynergyOpportunity],
        months: List[str]
    ) -> Dict[str, List[float]]:
        """Get trends broken down by synergy type"""

        trends_by_type = {}

        for synergy_type in SynergyType:
            type_synergies = [s for s in synergies if s.synergy_type == synergy_type]
            monthly_values = []

            for month in months:
                month_total = sum(
                    s.monthly_tracking.get(month, 0)
                    for s in type_synergies
                    if s.monthly_tracking
                )
                monthly_values.append(float(month_total))

            trends_by_type[synergy_type.value] = monthly_values

        return trends_by_type


class WorkstreamManagementService:
    """Service for managing integration workstreams and tasks"""

    def __init__(self, db: Session):
        self.db = db

    def create_task(
        self,
        organization_id: str,
        workstream_id: str,
        task_data: Dict[str, Any]
    ) -> IntegrationTask:
        """Create a new integration task"""

        task = IntegrationTask(
            organization_id=organization_id,
            workstream_id=workstream_id,
            task_name=task_data["task_name"],
            description=task_data.get("description"),
            priority=task_data.get("priority", TaskPriority.MEDIUM),
            assigned_to_user_id=task_data.get("assigned_to_user_id"),
            assigned_team=task_data.get("assigned_team"),
            status=TaskStatus.NOT_STARTED,
            planned_start_date=task_data.get("planned_start_date"),
            planned_end_date=task_data.get("planned_end_date"),
            estimated_hours=task_data.get("estimated_hours"),
            predecessor_tasks=task_data.get("predecessor_tasks", []),
            acceptance_criteria=task_data.get("acceptance_criteria", [])
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        # Update workstream task count
        self._update_workstream_counts(workstream_id)

        return task

    def update_task_status(
        self,
        task_id: str,
        organization_id: str,
        status: TaskStatus,
        completion_percent: Optional[int] = None,
        update_note: Optional[str] = None
    ) -> IntegrationTask:
        """Update task status and completion"""

        task = self.db.query(IntegrationTask).filter(
            and_(
                IntegrationTask.id == task_id,
                IntegrationTask.organization_id == organization_id,
                IntegrationTask.deleted_at.is_(None)
            )
        ).first()

        if not task:
            raise ValueError("Task not found")

        old_status = task.status
        task.status = status

        if completion_percent is not None:
            task.completion_percent = completion_percent

        # Update dates based on status changes
        if status == TaskStatus.IN_PROGRESS and not task.actual_start_date:
            task.actual_start_date = datetime.utcnow()
        elif status == TaskStatus.COMPLETED:
            task.actual_end_date = datetime.utcnow()
            task.completion_percent = 100

        # Add update note
        if update_note:
            updates = task.updates or []
            updates.append({
                "date": datetime.utcnow().isoformat(),
                "update": update_note,
                "status_change": f"{old_status.value} → {status.value}"
            })
            task.updates = updates

        self.db.commit()
        self.db.refresh(task)

        # Update workstream progress
        self._update_workstream_counts(task.workstream_id)

        return task

    def _update_workstream_counts(self, workstream_id: str):
        """Update workstream task counts and completion percentage"""

        workstream = self.db.query(IntegrationWorkstream).filter(
            IntegrationWorkstream.id == workstream_id
        ).first()

        if not workstream:
            return

        tasks = self.db.query(IntegrationTask).filter(
            and_(
                IntegrationTask.workstream_id == workstream_id,
                IntegrationTask.deleted_at.is_(None)
            )
        ).all()

        workstream.tasks_total = len(tasks)
        workstream.tasks_completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)

        if tasks:
            avg_completion = sum(t.completion_percent or 0 for t in tasks) / len(tasks)
            workstream.completion_percent = int(avg_completion)

        self.db.commit()

    def get_workstream_summary(
        self,
        workstream_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive workstream summary"""

        workstream = self.db.query(IntegrationWorkstream).filter(
            and_(
                IntegrationWorkstream.id == workstream_id,
                IntegrationWorkstream.organization_id == organization_id,
                IntegrationWorkstream.deleted_at.is_(None)
            )
        ).first()

        if not workstream:
            raise ValueError("Workstream not found")

        tasks = self.db.query(IntegrationTask).filter(
            and_(
                IntegrationTask.workstream_id == workstream_id,
                IntegrationTask.deleted_at.is_(None)
            )
        ).all()

        return {
            "workstream": {
                "id": workstream.id,
                "name": workstream.workstream_name,
                "type": workstream.workstream_type.value,
                "status": workstream.status.value,
                "completion_percent": workstream.completion_percent,
                "health_status": workstream.health_status
            },
            "tasks": {
                "total": len(tasks),
                "by_status": {
                    status.value: sum(1 for t in tasks if t.status == status)
                    for status in TaskStatus
                },
                "by_priority": {
                    priority.value: sum(1 for t in tasks if t.priority == priority)
                    for priority in TaskPriority
                },
                "blocked": sum(1 for t in tasks if t.status == TaskStatus.BLOCKED)
            },
            "timeline": {
                "on_time": sum(1 for t in tasks if t.planned_end_date and (not t.actual_end_date or t.actual_end_date <= t.planned_end_date)),
                "delayed": sum(1 for t in tasks if t.planned_end_date and t.actual_end_date and t.actual_end_date > t.planned_end_date),
                "overdue": sum(1 for t in tasks if t.planned_end_date and not t.actual_end_date and datetime.utcnow() > t.planned_end_date)
            }
        }


class RiskManagementService:
    """Service for integration risk management"""

    def __init__(self, db: Session):
        self.db = db

    def create_risk(
        self,
        organization_id: str,
        project_id: str,
        risk_data: Dict[str, Any]
    ) -> IntegrationRisk:
        """Create a new integration risk"""

        # Calculate risk score from probability and impact
        probability_scores = {"very_low": 1, "low": 2, "medium": 3, "high": 4, "very_high": 5}
        impact_scores = {"very_low": 1, "low": 2, "medium": 3, "high": 4, "very_high": 5}

        prob_score = probability_scores.get(risk_data.get("probability", "medium"), 3)
        impact_score = impact_scores.get(risk_data.get("impact", "medium"), 3)
        risk_score = prob_score * impact_score

        # Determine risk level
        if risk_score >= 16:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 12:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 6:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        risk = IntegrationRisk(
            organization_id=organization_id,
            project_id=project_id,
            risk_name=risk_data["risk_name"],
            description=risk_data.get("description"),
            category=risk_data.get("category"),
            probability=risk_data.get("probability", "medium"),
            impact=risk_data.get("impact", "medium"),
            risk_level=risk_level,
            risk_score=risk_score,
            potential_impact=risk_data.get("potential_impact"),
            financial_impact=risk_data.get("financial_impact"),
            mitigation_strategy=risk_data.get("mitigation_strategy"),
            contingency_plan=risk_data.get("contingency_plan"),
            owner_user_id=risk_data.get("owner_user_id"),
            status=RiskStatus.IDENTIFIED
        )

        self.db.add(risk)
        self.db.commit()
        self.db.refresh(risk)

        logger.info(f"Created risk {risk.id} for project {project_id} with level {risk_level.value}")

        return risk

    def get_risk_matrix(
        self,
        project_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get risk matrix data for visualization"""

        risks = self.db.query(IntegrationRisk).filter(
            and_(
                IntegrationRisk.project_id == project_id,
                IntegrationRisk.organization_id == organization_id,
                IntegrationRisk.is_active == True,
                IntegrationRisk.deleted_at.is_(None)
            )
        ).all()

        # Create 5x5 matrix
        matrix = [[[] for _ in range(5)] for _ in range(5)]

        probability_map = {"very_low": 0, "low": 1, "medium": 2, "high": 3, "very_high": 4}
        impact_map = {"very_low": 0, "low": 1, "medium": 2, "high": 3, "very_high": 4}

        for risk in risks:
            prob_idx = probability_map.get(risk.probability, 2)
            impact_idx = impact_map.get(risk.impact, 2)

            matrix[prob_idx][impact_idx].append({
                "id": risk.id,
                "name": risk.risk_name,
                "score": risk.risk_score,
                "level": risk.risk_level.value
            })

        return {
            "matrix": matrix,
            "summary": {
                "total_active": len(risks),
                "by_level": {
                    level.value: sum(1 for r in risks if r.risk_level == level)
                    for level in RiskLevel
                }
            }
        }


class PerformanceTrackingService:
    """Service for tracking integration performance metrics"""

    def __init__(self, db: Session):
        self.db = db

    def record_metric_value(
        self,
        metric_id: str,
        organization_id: str,
        value: Decimal,
        measurement_date: Optional[datetime] = None
    ) -> PerformanceMetric:
        """Record a new value for a performance metric"""

        metric = self.db.query(PerformanceMetric).filter(
            and_(
                PerformanceMetric.id == metric_id,
                PerformanceMetric.organization_id == organization_id,
                PerformanceMetric.deleted_at.is_(None)
            )
        ).first()

        if not metric:
            raise ValueError("Metric not found")

        # Update current value
        metric.current_value = value
        metric.last_measured_at = measurement_date or datetime.utcnow()

        # Add to historical values
        historical = metric.historical_values or {}
        date_key = (measurement_date or datetime.utcnow()).strftime("%Y-%m-%d")
        historical[date_key] = float(value)
        metric.historical_values = historical

        # Calculate variance from target
        if metric.target_value:
            variance = float((value - metric.target_value) / metric.target_value * 100)
            metric.variance_from_target = Decimal(str(round(variance, 2)))
            metric.is_on_track = abs(variance) <= 10  # Within 10% is considered on track

        self.db.commit()
        self.db.refresh(metric)

        return metric
