"""
Workflow Management Service for M&A SaaS Platform
Advanced team orchestration, task automation, and performance optimization
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import Session
import uuid
import json
from copy import deepcopy
from collections import defaultdict
import asyncio
import logging

from ..models.teams import (
    Team, TeamMember, TeamTask, TaskSubtask, TaskTimeLog, TeamMeeting,
    TeamChannel, TeamMessage, TeamMetrics, PerformanceReview,
    ExternalAdvisor, Skill, UserSkill, SkillCategory,
    TeamType, TeamStatus, TeamRole, TaskStatus, TaskPriority,
    SkillLevel, MeetingType, MeetingStatus
)
from ..models.deal import Deal
from ..models.negotiations import Negotiation
from ..models.user import User
from .workflow_engine import WorkflowEngine, TriggerType, ActionType

logger = logging.getLogger(__name__)


class TeamFormationEngine:
    """Advanced team formation based on skills, availability, and optimization"""

    def __init__(self, db: Session):
        self.db = db

    def recommend_team_composition(
        self,
        organization_id: str,
        deal_id: Optional[str] = None,
        required_skills: List[str] = None,
        team_size: int = 5,
        budget_limit: Optional[Decimal] = None,
        start_date: date = None,
        duration_weeks: int = 12
    ) -> Dict[str, Any]:
        """
        Recommend optimal team composition based on requirements

        Args:
            organization_id: Tenant ID
            deal_id: Optional deal ID for context
            required_skills: List of required skill names
            team_size: Target team size
            budget_limit: Budget constraint
            start_date: Team start date
            duration_weeks: Expected duration in weeks

        Returns:
            Dictionary with team recommendations and analysis
        """
        if not start_date:
            start_date = date.today()

        if not required_skills:
            required_skills = self._get_default_deal_skills()

        # Get available users with required skills
        available_users = self._find_available_users(
            organization_id, required_skills, start_date, duration_weeks
        )

        # Calculate optimal team composition
        optimal_teams = self._optimize_team_composition(
            available_users, required_skills, team_size, budget_limit
        )

        # Generate recommendations
        recommendations = []
        for i, team_option in enumerate(optimal_teams[:3]):  # Top 3 options
            recommendation = {
                'option': i + 1,
                'team_members': team_option['members'],
                'total_cost': team_option['cost'],
                'skill_coverage': team_option['skill_coverage'],
                'experience_score': team_option['experience_score'],
                'availability_conflicts': team_option['conflicts'],
                'recommendation_score': team_option['score']
            }
            recommendations.append(recommendation)

        return {
            'recommendations': recommendations,
            'skill_analysis': self._analyze_skill_gaps(required_skills, available_users),
            'cost_analysis': self._analyze_costs(optimal_teams),
            'risk_factors': self._identify_risk_factors(optimal_teams[0] if optimal_teams else None)
        }

    def auto_form_team(
        self,
        organization_id: str,
        team_name: str,
        deal_id: Optional[str] = None,
        team_requirements: Dict[str, Any] = None,
        created_by_id: Optional[str] = None
    ) -> Team:
        """
        Automatically form and create a team based on requirements

        Args:
            organization_id: Tenant ID
            team_name: Name for the new team
            deal_id: Optional deal ID
            team_requirements: Requirements specification
            created_by_id: User creating the team

        Returns:
            Created team instance
        """
        requirements = team_requirements or {}

        # Get team recommendations
        recommendations = self.recommend_team_composition(
            organization_id=organization_id,
            deal_id=deal_id,
            required_skills=requirements.get('required_skills', []),
            team_size=requirements.get('team_size', 5),
            budget_limit=requirements.get('budget_limit'),
            start_date=requirements.get('start_date', date.today()),
            duration_weeks=requirements.get('duration_weeks', 12)
        )

        if not recommendations['recommendations']:
            raise ValueError("Unable to form team with given requirements")

        # Use the best recommendation
        best_option = recommendations['recommendations'][0]

        # Create team
        team = Team(
            organization_id=organization_id,
            name=team_name,
            description=f"Auto-formed team for {team_name}",
            team_type=TeamType.DEAL_TEAM if deal_id else TeamType.PROJECT_TEAM,
            deal_id=deal_id,
            team_lead_id=best_option['team_members'][0]['user_id'],  # First member as lead
            target_team_size=len(best_option['team_members']),
            current_team_size=len(best_option['team_members']),
            budget_allocated=best_option['total_cost'],
            created_by=created_by_id
        )

        self.db.add(team)
        self.db.flush()  # Get team ID

        # Add team members
        for member_data in best_option['team_members']:
            team_member = TeamMember(
                organization_id=organization_id,
                team_id=team.id,
                user_id=member_data['user_id'],
                role=self._determine_role(member_data),
                allocation_percentage=member_data.get('allocation', 100),
                hourly_rate=member_data.get('hourly_rate'),
                primary_skills=member_data.get('skills', []),
                created_by=created_by_id
            )
            self.db.add(team_member)

        self.db.commit()
        self.db.refresh(team)

        # Create default team channel
        self._create_default_channel(team.id, organization_id, created_by_id)

        return team

    def _find_available_users(
        self,
        organization_id: str,
        required_skills: List[str],
        start_date: date,
        duration_weeks: int
    ) -> List[Dict[str, Any]]:
        """Find users with required skills and availability"""

        # Get users with required skills
        skill_query = (
            self.db.query(User, UserSkill, Skill)
            .join(UserSkill, User.id == UserSkill.user_id)
            .join(Skill, UserSkill.skill_id == Skill.id)
            .filter(
                User.organization_id == organization_id,
                Skill.name.in_(required_skills),
                User.is_deleted == False
            )
        )

        users_with_skills = defaultdict(list)
        for user, user_skill, skill in skill_query.all():
            users_with_skills[user.id].append({
                'user': user,
                'skill': skill.name,
                'level': user_skill.skill_level,
                'experience': user_skill.years_experience or 0
            })

        # Check availability for each user
        available_users = []
        end_date = start_date + timedelta(weeks=duration_weeks)

        for user_id, skills in users_with_skills.items():
            user = skills[0]['user']

            # Calculate current allocation
            current_allocation = self._calculate_user_allocation(user_id, start_date, end_date)

            if current_allocation < 100:  # User has some availability
                available_users.append({
                    'user_id': user_id,
                    'user': user,
                    'skills': [s['skill'] for s in skills],
                    'skill_levels': {s['skill']: s['level'] for s in skills},
                    'experience_years': sum(s['experience'] for s in skills),
                    'availability': 100 - current_allocation,
                    'hourly_rate': self._get_user_hourly_rate(user_id)
                })

        return available_users

    def _optimize_team_composition(
        self,
        available_users: List[Dict[str, Any]],
        required_skills: List[str],
        team_size: int,
        budget_limit: Optional[Decimal]
    ) -> List[Dict[str, Any]]:
        """Optimize team composition using scoring algorithm"""

        # Generate team combinations
        from itertools import combinations

        team_options = []

        # Try different combinations of users
        for team_combo in combinations(available_users, min(team_size, len(available_users))):
            team_analysis = self._analyze_team_combination(team_combo, required_skills, budget_limit)
            if team_analysis['is_viable']:
                team_options.append(team_analysis)

        # Sort by optimization score
        team_options.sort(key=lambda x: x['score'], reverse=True)

        return team_options[:10]  # Return top 10 options

    def _analyze_team_combination(
        self,
        team_members: Tuple[Dict[str, Any], ...],
        required_skills: List[str],
        budget_limit: Optional[Decimal]
    ) -> Dict[str, Any]:
        """Analyze a specific team combination"""

        # Calculate skill coverage
        covered_skills = set()
        skill_quality = {}
        total_experience = 0
        total_cost = Decimal('0')

        for member in team_members:
            covered_skills.update(member['skills'])
            total_experience += member['experience_years']

            # Calculate weekly cost (assuming 40 hours/week)
            if member['hourly_rate']:
                total_cost += Decimal(str(member['hourly_rate'])) * 40

            # Track best skill level for each skill
            for skill in member['skills']:
                current_level = skill_quality.get(skill, SkillLevel.BEGINNER)
                new_level = member['skill_levels'][skill]
                if self._skill_level_value(new_level) > self._skill_level_value(current_level):
                    skill_quality[skill] = new_level

        # Calculate metrics
        skill_coverage = len(covered_skills.intersection(required_skills)) / len(required_skills)
        experience_score = min(100, total_experience / len(team_members) * 10)  # Normalize to 0-100

        # Budget check
        budget_viable = budget_limit is None or total_cost <= budget_limit

        # Overall score
        score = (
            skill_coverage * 40 +  # 40% weight on skill coverage
            experience_score * 30 +  # 30% weight on experience
            (100 if budget_viable else 0) * 20 +  # 20% weight on budget
            min(100, sum(member['availability'] for member in team_members) / len(team_members)) * 10  # 10% availability
        )

        return {
            'members': [
                {
                    'user_id': m['user_id'],
                    'name': f"{m['user'].first_name} {m['user'].last_name}",
                    'skills': m['skills'],
                    'allocation': min(100, m['availability']),
                    'hourly_rate': m['hourly_rate']
                }
                for m in team_members
            ],
            'skill_coverage': skill_coverage,
            'experience_score': experience_score,
            'cost': total_cost,
            'is_viable': budget_viable and skill_coverage >= 0.8,  # At least 80% skill coverage
            'conflicts': [],  # TODO: Check for scheduling conflicts
            'score': score
        }

    def _get_default_deal_skills(self) -> List[str]:
        """Get default skills required for M&A deals"""
        return [
            "Financial Analysis",
            "Due Diligence",
            "Legal Review",
            "Valuation",
            "Project Management",
            "M&A Experience",
            "Industry Knowledge"
        ]

    def _calculate_user_allocation(self, user_id: str, start_date: date, end_date: date) -> float:
        """Calculate user's current allocation percentage"""

        # Get active team memberships during the period
        active_memberships = (
            self.db.query(TeamMember)
            .join(Team)
            .filter(
                TeamMember.user_id == user_id,
                TeamMember.is_active == True,
                Team.status.in_([TeamStatus.ACTIVE, TeamStatus.PERFORMING]),
                or_(
                    TeamMember.planned_end_date.is_(None),
                    TeamMember.planned_end_date >= start_date
                ),
                TeamMember.start_date <= end_date
            )
            .all()
        )

        total_allocation = sum(m.allocation_percentage for m in active_memberships)
        return min(100, total_allocation)  # Cap at 100%

    def _get_user_hourly_rate(self, user_id: str) -> Optional[Decimal]:
        """Get user's hourly rate from recent team memberships"""

        recent_membership = (
            self.db.query(TeamMember)
            .filter(
                TeamMember.user_id == user_id,
                TeamMember.hourly_rate.isnot(None)
            )
            .order_by(desc(TeamMember.created_at))
            .first()
        )

        return recent_membership.hourly_rate if recent_membership else None

    def _determine_role(self, member_data: Dict[str, Any]) -> TeamRole:
        """Determine appropriate role based on skills and experience"""

        skills = member_data.get('skills', [])
        experience = member_data.get('experience_years', 0)

        # Simple role assignment logic
        if experience >= 10:
            return TeamRole.SENIOR_ANALYST
        elif experience >= 5:
            return TeamRole.ANALYST
        elif "Legal" in str(skills):
            return TeamRole.LEGAL_COUNSEL
        elif "Financial" in str(skills):
            return TeamRole.FINANCIAL_ADVISOR
        else:
            return TeamRole.ANALYST

    def _skill_level_value(self, level: SkillLevel) -> int:
        """Convert skill level to numeric value for comparison"""
        level_values = {
            SkillLevel.BEGINNER: 1,
            SkillLevel.INTERMEDIATE: 2,
            SkillLevel.ADVANCED: 3,
            SkillLevel.EXPERT: 4,
            SkillLevel.MASTER: 5
        }
        return level_values.get(level, 1)

    def _analyze_skill_gaps(self, required_skills: List[str], available_users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze skill gaps in available users"""

        available_skills = set()
        for user in available_users:
            available_skills.update(user['skills'])

        missing_skills = set(required_skills) - available_skills

        return {
            'missing_skills': list(missing_skills),
            'coverage_percentage': (len(set(required_skills) & available_skills) / len(required_skills)) * 100,
            'recommendations': [
                f"Consider external consultant for {skill}" for skill in missing_skills
            ] if missing_skills else []
        }

    def _analyze_costs(self, team_options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cost implications of team options"""

        if not team_options:
            return {}

        costs = [option['cost'] for option in team_options]

        return {
            'min_cost': min(costs),
            'max_cost': max(costs),
            'avg_cost': sum(costs) / len(costs),
            'cost_range': max(costs) - min(costs)
        }

    def _identify_risk_factors(self, team_option: Optional[Dict[str, Any]]) -> List[str]:
        """Identify potential risk factors for team composition"""

        if not team_option:
            return ["No viable team composition found"]

        risks = []

        if team_option['skill_coverage'] < 0.9:
            risks.append("Incomplete skill coverage - may need external consultants")

        if team_option['experience_score'] < 50:
            risks.append("Low average experience level - may need senior oversight")

        if len(team_option['members']) < 3:
            risks.append("Small team size - limited redundancy and knowledge sharing")

        return risks

    def _create_default_channel(self, team_id: str, organization_id: str, created_by_id: str):
        """Create default communication channel for new team"""

        channel = TeamChannel(
            organization_id=organization_id,
            team_id=team_id,
            name="general",
            description="General team communication",
            channel_type="general",
            created_by=created_by_id
        )
        self.db.add(channel)


class TaskOrchestrationEngine:
    """Advanced task management with dependencies and automation"""

    def __init__(self, db: Session):
        self.db = db

    def auto_create_deal_tasks(
        self,
        organization_id: str,
        team_id: str,
        deal_id: str,
        deal_type: str = "acquisition",
        created_by_id: Optional[str] = None
    ) -> List[TeamTask]:
        """
        Automatically create standard tasks for a deal based on type

        Args:
            organization_id: Tenant ID
            team_id: Team ID
            deal_id: Deal ID
            deal_type: Type of deal (acquisition, merger, etc.)
            created_by_id: User creating the tasks

        Returns:
            List of created tasks
        """

        # Get task templates based on deal type
        task_templates = self._get_deal_task_templates(deal_type)

        created_tasks = []
        task_dependencies = {}

        # Create tasks
        for template in task_templates:
            task = TeamTask(
                organization_id=organization_id,
                team_id=team_id,
                deal_id=deal_id,
                title=template['title'],
                description=template['description'],
                priority=TaskPriority(template.get('priority', 'medium')),
                estimated_hours=template.get('estimated_hours'),
                deliverables=template.get('deliverables', []),
                acceptance_criteria=template.get('acceptance_criteria'),
                created_by=created_by_id
            )

            self.db.add(task)
            self.db.flush()  # Get task ID

            created_tasks.append(task)
            task_dependencies[template['template_id']] = {
                'task': task,
                'depends_on': template.get('depends_on', [])
            }

        # Set up dependencies
        for template_id, task_info in task_dependencies.items():
            task = task_info['task']
            depends_on_templates = task_info['depends_on']

            dependency_task_ids = []
            for dep_template in depends_on_templates:
                if dep_template in task_dependencies:
                    dependency_task_ids.append(task_dependencies[dep_template]['task'].id)

            task.depends_on = dependency_task_ids

        # Auto-assign tasks based on team member skills
        self._auto_assign_tasks(created_tasks, team_id, organization_id)

        self.db.commit()
        return created_tasks

    def optimize_task_schedule(
        self,
        organization_id: str,
        team_id: str,
        target_completion_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Optimize task scheduling considering dependencies and resource availability

        Args:
            organization_id: Tenant ID
            team_id: Team ID
            target_completion_date: Target completion date

        Returns:
            Optimization results and recommendations
        """

        # Get all tasks for the team
        tasks = (
            self.db.query(TeamTask)
            .filter(
                TeamTask.team_id == team_id,
                TeamTask.organization_id == organization_id,
                TeamTask.status != TaskStatus.COMPLETED
            )
            .all()
        )

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(tasks)

        # Calculate critical path
        critical_path = self._calculate_critical_path(dependency_graph)

        # Optimize resource allocation
        resource_optimization = self._optimize_resource_allocation(tasks, team_id)

        # Generate schedule recommendations
        schedule_recommendations = self._generate_schedule_recommendations(
            tasks, critical_path, target_completion_date
        )

        return {
            'critical_path': critical_path,
            'estimated_completion_date': self._calculate_estimated_completion(critical_path),
            'resource_optimization': resource_optimization,
            'schedule_recommendations': schedule_recommendations,
            'bottlenecks': self._identify_bottlenecks(tasks, dependency_graph),
            'optimization_score': self._calculate_optimization_score(tasks)
        }

    def auto_assign_task(
        self,
        task_id: str,
        organization_id: str,
        assignment_criteria: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Automatically assign a task to the best available team member

        Args:
            task_id: Task ID
            organization_id: Tenant ID
            assignment_criteria: Optional criteria for assignment

        Returns:
            User ID of assigned team member, or None if no suitable assignment
        """

        task = (
            self.db.query(TeamTask)
            .filter(
                TeamTask.id == task_id,
                TeamTask.organization_id == organization_id
            )
            .first()
        )

        if not task or task.assignee_id:
            return None

        # Get team members
        team_members = (
            self.db.query(TeamMember)
            .filter(
                TeamMember.team_id == task.team_id,
                TeamMember.is_active == True,
                TeamMember.organization_id == organization_id
            )
            .all()
        )

        # Score each team member for this task
        best_member = None
        best_score = 0

        for member in team_members:
            score = self._calculate_assignment_score(task, member, assignment_criteria)
            if score > best_score:
                best_score = score
                best_member = member

        if best_member and best_score > 50:  # Minimum score threshold
            task.assignee_id = best_member.user_id
            self.db.commit()
            return best_member.user_id

        return None

    def _get_deal_task_templates(self, deal_type: str) -> List[Dict[str, Any]]:
        """Get standard task templates for deal type"""

        # Base templates for M&A deals
        templates = [
            {
                'template_id': 'initial_review',
                'title': 'Initial Deal Review',
                'description': 'Conduct initial review of deal opportunity and target company',
                'priority': 'high',
                'estimated_hours': 16,
                'deliverables': ['Initial Assessment Report', 'Go/No-Go Recommendation'],
                'acceptance_criteria': 'Completed initial assessment with documented recommendation',
                'depends_on': []
            },
            {
                'template_id': 'nda_execution',
                'title': 'Execute NDA',
                'description': 'Prepare and execute Non-Disclosure Agreement',
                'priority': 'high',
                'estimated_hours': 8,
                'deliverables': ['Executed NDA'],
                'acceptance_criteria': 'Signed NDA from all parties',
                'depends_on': ['initial_review']
            },
            {
                'template_id': 'financial_analysis',
                'title': 'Financial Analysis',
                'description': 'Analyze target company financial statements and performance',
                'priority': 'high',
                'estimated_hours': 40,
                'deliverables': ['Financial Analysis Report', 'Financial Model'],
                'acceptance_criteria': 'Completed financial analysis with model and recommendations',
                'depends_on': ['nda_execution']
            },
            {
                'template_id': 'market_analysis',
                'title': 'Market Analysis',
                'description': 'Analyze market conditions and competitive landscape',
                'priority': 'medium',
                'estimated_hours': 24,
                'deliverables': ['Market Analysis Report'],
                'acceptance_criteria': 'Completed market analysis with insights and implications',
                'depends_on': ['nda_execution']
            },
            {
                'template_id': 'legal_review',
                'title': 'Legal Due Diligence',
                'description': 'Conduct legal review of corporate structure and compliance',
                'priority': 'high',
                'estimated_hours': 60,
                'deliverables': ['Legal DD Report', 'Risk Assessment'],
                'acceptance_criteria': 'Completed legal review with identified risks and mitigations',
                'depends_on': ['nda_execution']
            },
            {
                'template_id': 'valuation',
                'title': 'Valuation Analysis',
                'description': 'Perform comprehensive valuation using multiple methodologies',
                'priority': 'critical',
                'estimated_hours': 48,
                'deliverables': ['Valuation Report', 'Sensitivity Analysis'],
                'acceptance_criteria': 'Completed valuation with range and recommendations',
                'depends_on': ['financial_analysis', 'market_analysis']
            },
            {
                'template_id': 'loi_preparation',
                'title': 'Letter of Intent Preparation',
                'description': 'Prepare Letter of Intent based on analysis and valuation',
                'priority': 'high',
                'estimated_hours': 16,
                'deliverables': ['Draft LOI', 'Terms Summary'],
                'acceptance_criteria': 'LOI ready for negotiation',
                'depends_on': ['valuation', 'legal_review']
            },
            {
                'template_id': 'final_due_diligence',
                'title': 'Final Due Diligence',
                'description': 'Conduct comprehensive due diligence across all areas',
                'priority': 'critical',
                'estimated_hours': 120,
                'deliverables': ['DD Report', 'Risk Matrix', 'Integration Plan'],
                'acceptance_criteria': 'Completed comprehensive due diligence',
                'depends_on': ['loi_preparation']
            }
        ]

        # Add deal-type specific templates
        if deal_type == "merger":
            templates.extend([
                {
                    'template_id': 'regulatory_approval',
                    'title': 'Regulatory Approval Process',
                    'description': 'Manage regulatory approval process for merger',
                    'priority': 'critical',
                    'estimated_hours': 80,
                    'deliverables': ['Regulatory Filing', 'Approval Timeline'],
                    'acceptance_criteria': 'Regulatory approvals obtained',
                    'depends_on': ['final_due_diligence']
                }
            ])

        return templates

    def _auto_assign_tasks(
        self,
        tasks: List[TeamTask],
        team_id: str,
        organization_id: str
    ):
        """Automatically assign tasks based on team member skills"""

        # Get team members with skills
        team_members = (
            self.db.query(TeamMember, UserSkill, Skill)
            .outerjoin(UserSkill, TeamMember.user_id == UserSkill.user_id)
            .outerjoin(Skill, UserSkill.skill_id == Skill.id)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.is_active == True,
                TeamMember.organization_id == organization_id
            )
            .all()
        )

        # Build member skill profiles
        member_skills = defaultdict(list)
        for member, user_skill, skill in team_members:
            if skill:
                member_skills[member.user_id].append({
                    'skill': skill.name,
                    'level': user_skill.skill_level
                })

        # Assign tasks based on best skill match
        for task in tasks:
            best_assignee = self._find_best_assignee(task, member_skills)
            if best_assignee:
                task.assignee_id = best_assignee

    def _find_best_assignee(
        self,
        task: TeamTask,
        member_skills: Dict[str, List[Dict[str, Any]]]
    ) -> Optional[str]:
        """Find best assignee for a task based on skills"""

        # Define skill requirements for different task types
        skill_requirements = {
            'Financial Analysis': ['Financial Analysis', 'Accounting', 'Valuation'],
            'Legal': ['Legal Review', 'Corporate Law', 'Contract Review'],
            'Market Analysis': ['Market Research', 'Industry Analysis', 'Competitive Analysis'],
            'Due Diligence': ['Due Diligence', 'Risk Assessment', 'Audit'],
            'Valuation': ['Valuation', 'Financial Modeling', 'DCF Analysis']
        }

        # Determine required skills for task
        required_skills = []
        for skill_type, skills in skill_requirements.items():
            if skill_type.lower() in task.title.lower():
                required_skills.extend(skills)

        if not required_skills:
            # Default assignment logic if no specific skills identified
            return list(member_skills.keys())[0] if member_skills else None

        # Score each member
        best_member = None
        best_score = 0

        for member_id, skills in member_skills.items():
            score = 0
            member_skill_names = [s['skill'] for s in skills]

            for req_skill in required_skills:
                if req_skill in member_skill_names:
                    # Find skill level and add to score
                    skill_info = next(s for s in skills if s['skill'] == req_skill)
                    score += self._skill_level_value(skill_info['level'])

            if score > best_score:
                best_score = score
                best_member = member_id

        return best_member

    def _build_dependency_graph(self, tasks: List[TeamTask]) -> Dict[str, Dict[str, Any]]:
        """Build dependency graph for tasks"""

        graph = {}

        for task in tasks:
            graph[task.id] = {
                'task': task,
                'dependencies': task.depends_on or [],
                'dependents': []
            }

        # Build reverse dependencies (dependents)
        for task_id, task_info in graph.items():
            for dep_id in task_info['dependencies']:
                if dep_id in graph:
                    graph[dep_id]['dependents'].append(task_id)

        return graph

    def _calculate_critical_path(self, dependency_graph: Dict[str, Dict[str, Any]]) -> List[str]:
        """Calculate critical path through task dependencies"""

        # Simplified critical path calculation
        # In production, this would use proper CPM algorithm

        def calculate_longest_path(task_id: str, visited: Set[str] = None) -> int:
            if visited is None:
                visited = set()

            if task_id in visited:
                return 0  # Circular dependency

            visited.add(task_id)
            task_info = dependency_graph.get(task_id)
            if not task_info:
                return 0

            task = task_info['task']
            task_duration = float(task.estimated_hours or 8)  # Default 8 hours

            max_dependency_path = 0
            for dep_id in task_info['dependencies']:
                dep_path = calculate_longest_path(dep_id, visited.copy())
                max_dependency_path = max(max_dependency_path, dep_path)

            return task_duration + max_dependency_path

        # Find critical path
        critical_tasks = []
        max_path_length = 0

        for task_id in dependency_graph:
            path_length = calculate_longest_path(task_id)
            if path_length > max_path_length:
                max_path_length = path_length
                # In a full implementation, we'd track the actual path
                critical_tasks = [task_id]  # Simplified

        return critical_tasks

    def _calculate_assignment_score(
        self,
        task: TeamTask,
        member: TeamMember,
        criteria: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate assignment score for a member-task combination"""

        score = 50  # Base score

        # Skill match scoring
        task_skills = self._extract_task_skills(task)
        member_skills = member.primary_skills or []

        skill_matches = len(set(task_skills) & set(member_skills))
        score += skill_matches * 20  # 20 points per matching skill

        # Availability scoring
        if member.allocation_percentage < 90:
            score += 20  # Bonus for availability
        elif member.allocation_percentage >= 100:
            score -= 30  # Penalty for overallocation

        # Experience scoring (based on performance rating)
        if member.performance_rating:
            score += float(member.performance_rating) * 5

        # Role appropriateness
        if self._is_role_appropriate(task, member.role):
            score += 15

        return min(100, max(0, score))

    def _extract_task_skills(self, task: TeamTask) -> List[str]:
        """Extract required skills from task title and description"""

        skill_keywords = {
            'financial': ['Financial Analysis', 'Accounting'],
            'legal': ['Legal Review', 'Corporate Law'],
            'market': ['Market Research', 'Industry Analysis'],
            'valuation': ['Valuation', 'Financial Modeling'],
            'due diligence': ['Due Diligence', 'Risk Assessment']
        }

        task_text = f"{task.title} {task.description or ''}".lower()
        required_skills = []

        for keyword, skills in skill_keywords.items():
            if keyword in task_text:
                required_skills.extend(skills)

        return required_skills

    def _is_role_appropriate(self, task: TeamTask, role: TeamRole) -> bool:
        """Check if role is appropriate for task"""

        role_task_mapping = {
            TeamRole.LEGAL_COUNSEL: ['legal', 'contract', 'compliance'],
            TeamRole.FINANCIAL_ADVISOR: ['financial', 'valuation', 'modeling'],
            TeamRole.SENIOR_ANALYST: ['analysis', 'research', 'review'],
            TeamRole.DEAL_LEAD: ['coordination', 'management', 'oversight']
        }

        task_text = f"{task.title} {task.description or ''}".lower()
        appropriate_keywords = role_task_mapping.get(role, [])

        return any(keyword in task_text for keyword in appropriate_keywords)

    def _skill_level_value(self, level: SkillLevel) -> int:
        """Convert skill level to numeric value"""
        level_values = {
            SkillLevel.BEGINNER: 1,
            SkillLevel.INTERMEDIATE: 2,
            SkillLevel.ADVANCED: 3,
            SkillLevel.EXPERT: 4,
            SkillLevel.MASTER: 5
        }
        return level_values.get(level, 1)

    def _optimize_resource_allocation(self, tasks: List[TeamTask], team_id: str) -> Dict[str, Any]:
        """Optimize resource allocation across tasks"""

        # Get team capacity
        team_members = (
            self.db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.is_active == True
            )
            .all()
        )

        total_capacity = sum(m.availability_hours_per_week or 40 for m in team_members)
        total_demand = sum(float(t.estimated_hours or 8) for t in tasks)

        utilization_rate = (total_demand / total_capacity) * 100 if total_capacity > 0 else 0

        recommendations = []
        if utilization_rate > 90:
            recommendations.append("Team is over-allocated - consider extending timeline or adding resources")
        elif utilization_rate < 60:
            recommendations.append("Team has excess capacity - consider additional scope or reducing team size")

        return {
            'total_capacity_hours': total_capacity,
            'total_demand_hours': total_demand,
            'utilization_rate': utilization_rate,
            'recommendations': recommendations,
            'resource_gaps': self._identify_resource_gaps(tasks, team_members)
        }

    def _identify_resource_gaps(self, tasks: List[TeamTask], team_members: List[TeamMember]) -> List[str]:
        """Identify gaps in resource allocation"""

        gaps = []

        # Check for unassigned tasks
        unassigned_tasks = [t for t in tasks if not t.assignee_id]
        if unassigned_tasks:
            gaps.append(f"{len(unassigned_tasks)} tasks remain unassigned")

        # Check for overallocated members
        member_allocations = defaultdict(int)
        for task in tasks:
            if task.assignee_id:
                member_allocations[task.assignee_id] += float(task.estimated_hours or 8)

        for member in team_members:
            if member.user_id in member_allocations:
                allocated_hours = member_allocations[member.user_id]
                available_hours = member.availability_hours_per_week or 40
                if allocated_hours > available_hours:
                    gaps.append(f"Team member overallocated by {allocated_hours - available_hours} hours")

        return gaps

    def _generate_schedule_recommendations(
        self,
        tasks: List[TeamTask],
        critical_path: List[str],
        target_date: Optional[date]
    ) -> List[str]:
        """Generate schedule optimization recommendations"""

        recommendations = []

        # Check for missing due dates
        missing_dates = [t for t in tasks if not t.due_date]
        if missing_dates:
            recommendations.append(f"Set due dates for {len(missing_dates)} tasks")

        # Check for overdue tasks
        overdue_tasks = [t for t in tasks if t.due_date and t.due_date < date.today() and t.status != TaskStatus.COMPLETED]
        if overdue_tasks:
            recommendations.append(f"Address {len(overdue_tasks)} overdue tasks immediately")

        # Check critical path
        if critical_path:
            recommendations.append("Focus on critical path tasks to avoid delays")

        return recommendations

    def _calculate_estimated_completion(self, critical_path: List[str]) -> Optional[date]:
        """Calculate estimated completion date based on critical path"""

        if not critical_path:
            return None

        # Simplified calculation - in production would be more sophisticated
        total_hours = 0
        for task_id in critical_path:
            task = self.db.query(TeamTask).filter(TeamTask.id == task_id).first()
            if task:
                total_hours += float(task.estimated_hours or 8)

        # Assume 40 hours per week
        weeks_needed = total_hours / 40
        return date.today() + timedelta(weeks=weeks_needed)

    def _identify_bottlenecks(self, tasks: List[TeamTask], dependency_graph: Dict[str, Dict[str, Any]]) -> List[str]:
        """Identify potential bottlenecks in task flow"""

        bottlenecks = []

        # Find tasks with many dependents
        for task_id, task_info in dependency_graph.items():
            if len(task_info['dependents']) >= 3:
                task = task_info['task']
                bottlenecks.append(f"Task '{task.title}' blocks {len(task_info['dependents'])} other tasks")

        # Find overallocated assignees
        assignee_tasks = defaultdict(list)
        for task in tasks:
            if task.assignee_id:
                assignee_tasks[task.assignee_id].append(task)

        for assignee_id, assignee_tasks_list in assignee_tasks.items():
            if len(assignee_tasks_list) >= 5:  # Arbitrary threshold
                bottlenecks.append(f"Team member has {len(assignee_tasks_list)} assigned tasks")

        return bottlenecks

    def _calculate_optimization_score(self, tasks: List[TeamTask]) -> float:
        """Calculate overall optimization score for task allocation"""

        total_tasks = len(tasks)
        if total_tasks == 0:
            return 100

        # Count positive factors
        assigned_tasks = len([t for t in tasks if t.assignee_id])
        tasks_with_dates = len([t for t in tasks if t.due_date])
        tasks_with_estimates = len([t for t in tasks if t.estimated_hours])

        # Calculate score
        assignment_score = (assigned_tasks / total_tasks) * 40  # 40% weight
        scheduling_score = (tasks_with_dates / total_tasks) * 30  # 30% weight
        planning_score = (tasks_with_estimates / total_tasks) * 30  # 30% weight

        return assignment_score + scheduling_score + planning_score


class WorkflowManagementService:
    """Main service orchestrating team formation and task management"""

    def __init__(self, db: Session):
        self.db = db
        self.team_formation = TeamFormationEngine(db)
        self.task_orchestration = TaskOrchestrationEngine(db)
        self.workflow_engine = WorkflowEngine(db)

    async def create_deal_workflow(
        self,
        organization_id: str,
        deal_id: str,
        workflow_config: Dict[str, Any],
        created_by_id: str
    ) -> Dict[str, Any]:
        """
        Create complete deal workflow with team formation and task orchestration

        Args:
            organization_id: Tenant ID
            deal_id: Deal ID
            workflow_config: Configuration for workflow creation
            created_by_id: User creating the workflow

        Returns:
            Created workflow information
        """

        # Form team
        team = self.team_formation.auto_form_team(
            organization_id=organization_id,
            team_name=workflow_config.get('team_name', f"Deal Team - {deal_id}"),
            deal_id=deal_id,
            team_requirements=workflow_config.get('team_requirements', {}),
            created_by_id=created_by_id
        )

        # Create tasks
        tasks = self.task_orchestration.auto_create_deal_tasks(
            organization_id=organization_id,
            team_id=team.id,
            deal_id=deal_id,
            deal_type=workflow_config.get('deal_type', 'acquisition'),
            created_by_id=created_by_id
        )

        # Optimize schedule
        optimization = self.task_orchestration.optimize_task_schedule(
            organization_id=organization_id,
            team_id=team.id,
            target_completion_date=workflow_config.get('target_completion_date')
        )

        # Set up workflow automation
        await self._setup_workflow_automation(team.id, deal_id, organization_id)

        return {
            'team': team,
            'tasks': tasks,
            'optimization': optimization,
            'estimated_completion': optimization.get('estimated_completion_date'),
            'recommendations': optimization.get('schedule_recommendations', [])
        }

    async def _setup_workflow_automation(self, team_id: str, deal_id: str, organization_id: str):
        """Set up automated workflow triggers and actions"""

        # Example automation rules
        automation_rules = [
            {
                'name': 'Task Completion Notification',
                'trigger': {
                    'type': TriggerType.DATA_CHANGE,
                    'conditions': [
                        {'field': 'status', 'operator': 'equals', 'value': TaskStatus.COMPLETED}
                    ]
                },
                'actions': [
                    {
                        'type': ActionType.SEND_NOTIFICATION,
                        'config': {
                            'recipients': ['team_lead'],
                            'message': 'Task completed: {task_title}'
                        }
                    },
                    {
                        'type': ActionType.UPDATE_RECORD,
                        'config': {
                            'model': 'TeamMetrics',
                            'updates': {'tasks_completed': '+1'}
                        }
                    }
                ]
            },
            {
                'name': 'Overdue Task Alert',
                'trigger': {
                    'type': TriggerType.SCHEDULE,
                    'schedule': 'daily',
                    'conditions': [
                        {'field': 'due_date', 'operator': 'less_than', 'value': 'today'}
                    ]
                },
                'actions': [
                    {
                        'type': ActionType.SEND_EMAIL,
                        'config': {
                            'recipients': ['assignee', 'team_lead'],
                            'subject': 'Overdue Task Alert',
                            'template': 'overdue_task_alert'
                        }
                    }
                ]
            }
        ]

        # Register automation rules with workflow engine
        for rule in automation_rules:
            await self.workflow_engine.create_workflow(
                name=rule['name'],
                trigger_config=rule['trigger'],
                actions=rule['actions'],
                organization_id=organization_id
            )