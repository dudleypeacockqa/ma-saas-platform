"""
Workflow Automation Engine
Cross-platform trigger-action sequences with conditional logic
"""

import os
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import asyncio
import json
from enum import Enum
from sqlalchemy.orm import Session
import re

from app.agents.integration_agent import get_integration_agent

logger = logging.getLogger(__name__)


class TriggerType(str, Enum):
    """Types of workflow triggers"""
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"
    API_CALL = "api_call"
    MANUAL = "manual"
    EVENT = "event"
    DATA_CHANGE = "data_change"
    TIME_BASED = "time_based"


class ActionType(str, Enum):
    """Types of workflow actions"""
    API_CALL = "api_call"
    SEND_EMAIL = "send_email"
    SEND_NOTIFICATION = "send_notification"
    CREATE_RECORD = "create_record"
    UPDATE_RECORD = "update_record"
    DELETE_RECORD = "delete_record"
    PUBLISH_CONTENT = "publish_content"
    SYNC_DATA = "sync_data"
    RUN_SCRIPT = "run_script"
    WAIT = "wait"
    CONDITION = "condition"
    LOOP = "loop"


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class Trigger:
    """Base class for workflow triggers"""

    def __init__(self, trigger_config: Dict[str, Any]):
        self.config = trigger_config
        self.trigger_type = trigger_config.get("type", TriggerType.MANUAL)

    async def should_execute(self, event_data: Optional[Dict[str, Any]] = None) -> bool:
        """Check if trigger conditions are met"""
        conditions = self.config.get("conditions", [])

        if not conditions:
            return True

        for condition in conditions:
            if not self._evaluate_condition(condition, event_data):
                return False

        return True

    def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        event_data: Optional[Dict[str, Any]]
    ) -> bool:
        """Evaluate a single condition"""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        if not event_data or field not in event_data:
            return False

        actual_value = event_data.get(field)

        # Operators
        if operator == "equals":
            return actual_value == value
        elif operator == "not_equals":
            return actual_value != value
        elif operator == "contains":
            return value in str(actual_value)
        elif operator == "greater_than":
            return float(actual_value) > float(value)
        elif operator == "less_than":
            return float(actual_value) < float(value)
        elif operator == "in":
            return actual_value in value
        elif operator == "not_in":
            return actual_value not in value
        elif operator == "regex":
            return bool(re.match(value, str(actual_value)))

        return False


class Action:
    """Base class for workflow actions"""

    def __init__(self, action_config: Dict[str, Any]):
        self.config = action_config
        self.action_type = action_config.get("type", ActionType.API_CALL)

    async def execute(
        self,
        context: Dict[str, Any],
        organization_id: str
    ) -> Dict[str, Any]:
        """Execute the action"""
        raise NotImplementedError("Subclasses must implement execute()")


class PublishContentAction(Action):
    """Action to publish content to social media platforms"""

    async def execute(
        self,
        context: Dict[str, Any],
        organization_id: str
    ) -> Dict[str, Any]:
        """Publish content to specified platforms"""
        content = self.config.get("content") or context.get("content", "")
        platforms = self.config.get("platforms", [])

        # Get integration agent
        agent = get_integration_agent(organization_id)

        # Publish to all platforms
        results = await agent.cross_platform_publish(
            content=content,
            platforms=platforms,
            content_type=self.config.get("content_type", "post"),
            metadata=self.config.get("metadata", {})
        )

        return {
            "action": "publish_content",
            "success": all(results.values()),
            "platforms": platforms,
            "results": results
        }


class SyncDataAction(Action):
    """Action to synchronize data from a platform"""

    async def execute(
        self,
        context: Dict[str, Any],
        organization_id: str
    ) -> Dict[str, Any]:
        """Sync data from platform"""
        platform = self.config.get("platform")
        sync_type = self.config.get("sync_type", "all")

        # Get integration agent
        agent = get_integration_agent(organization_id)

        # Sync data
        result = await agent.sync_platform_data(
            platform_name=platform,
            sync_type=sync_type,
            since=context.get("since")
        )

        return {
            "action": "sync_data",
            "platform": platform,
            "sync_type": sync_type,
            **result
        }


class APICallAction(Action):
    """Action to make an API call"""

    async def execute(
        self,
        context: Dict[str, Any],
        organization_id: str
    ) -> Dict[str, Any]:
        """Make API call"""
        import httpx

        url = self.config.get("url")
        method = self.config.get("method", "GET")
        headers = self.config.get("headers", {})
        body = self.config.get("body", {})

        # Replace variables in URL, headers, and body
        url = self._replace_variables(url, context)
        headers = self._replace_variables(headers, context)
        body = self._replace_variables(body, context)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body if method in ["POST", "PUT", "PATCH"] else None
                )

                return {
                    "action": "api_call",
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                }

        except Exception as e:
            logger.error(f"API call failed: {e}")
            return {
                "action": "api_call",
                "success": False,
                "error": str(e)
            }

    def _replace_variables(self, data: Any, context: Dict[str, Any]) -> Any:
        """Replace {{variable}} placeholders with context values"""
        if isinstance(data, str):
            for key, value in context.items():
                data = data.replace(f"{{{{{key}}}}}", str(value))
            return data
        elif isinstance(data, dict):
            return {k: self._replace_variables(v, context) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_variables(item, context) for item in data]
        return data


class WaitAction(Action):
    """Action to wait for a specified duration"""

    async def execute(
        self,
        context: Dict[str, Any],
        organization_id: str
    ) -> Dict[str, Any]:
        """Wait for specified duration"""
        duration_seconds = self.config.get("duration_seconds", 60)

        await asyncio.sleep(duration_seconds)

        return {
            "action": "wait",
            "success": True,
            "duration_seconds": duration_seconds
        }


class ConditionAction(Action):
    """Action to evaluate a condition and branch"""

    async def execute(
        self,
        context: Dict[str, Any],
        organization_id: str
    ) -> Dict[str, Any]:
        """Evaluate condition"""
        condition = self.config.get("condition", {})
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        actual_value = context.get(field)

        # Evaluate
        result = False
        if operator == "equals":
            result = actual_value == value
        elif operator == "greater_than":
            result = float(actual_value) > float(value)
        elif operator == "less_than":
            result = float(actual_value) < float(value)
        elif operator == "contains":
            result = value in str(actual_value)

        return {
            "action": "condition",
            "success": True,
            "condition_met": result,
            "true_branch": self.config.get("true_actions", []),
            "false_branch": self.config.get("false_actions", [])
        }


class WorkflowEngine:
    """
    Main workflow execution engine
    Executes trigger-action sequences with conditional logic
    """

    # Action registry
    ACTION_REGISTRY: Dict[str, type] = {
        ActionType.PUBLISH_CONTENT: PublishContentAction,
        ActionType.SYNC_DATA: SyncDataAction,
        ActionType.API_CALL: APICallAction,
        ActionType.WAIT: WaitAction,
        ActionType.CONDITION: ConditionAction
    }

    def __init__(self, db: Session):
        self.db = db

    async def execute_workflow(
        self,
        workflow_id: str,
        organization_id: str,
        trigger_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete workflow

        Args:
            workflow_id: ID of the workflow to execute
            organization_id: Organization ID
            trigger_data: Data that triggered the workflow
            context: Initial execution context

        Returns:
            Execution result summary
        """
        from app.models.integrations import WorkflowAutomation, WorkflowExecution

        # Get workflow definition
        workflow = self.db.query(WorkflowAutomation).filter(
            WorkflowAutomation.id == workflow_id,
            WorkflowAutomation.organization_id == organization_id,
            WorkflowAutomation.is_active == True
        ).first()

        if not workflow:
            return {
                "success": False,
                "error": "Workflow not found or not active"
            }

        # Create execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            organization_id=organization_id,
            triggered_by="system",
            trigger_data=trigger_data or {},
            status=WorkflowStatus.RUNNING,
            total_steps=workflow.action_count
        )
        self.db.add(execution)
        self.db.commit()

        # Initialize context
        exec_context = context or {}
        exec_context.update(trigger_data or {})
        exec_context["workflow_id"] = workflow_id
        exec_context["execution_id"] = execution.id

        # Execute workflow
        try:
            # Check trigger conditions
            trigger = Trigger(workflow.trigger_config)
            if not await trigger.should_execute(trigger_data):
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
                self.db.commit()

                return {
                    "success": True,
                    "skipped": True,
                    "reason": "Trigger conditions not met"
                }

            # Execute actions
            results = await self._execute_actions(
                workflow.actions,
                exec_context,
                organization_id,
                execution
            )

            # Update execution record
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.duration_ms = int((execution.completed_at - execution.started_at).total_seconds() * 1000)
            execution.action_results = results
            execution.output_data = exec_context

            # Update workflow statistics
            workflow.execution_count += 1
            workflow.successful_executions += 1
            workflow.last_executed_at = datetime.utcnow()
            workflow.last_success_at = datetime.utcnow()

            self.db.commit()

            return {
                "success": True,
                "execution_id": execution.id,
                "results": results,
                "duration_ms": execution.duration_ms
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")

            # Update execution record
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)

            # Update workflow statistics
            workflow.execution_count += 1
            workflow.failed_executions += 1
            workflow.last_failure_at = datetime.utcnow()

            self.db.commit()

            return {
                "success": False,
                "execution_id": execution.id,
                "error": str(e)
            }

    async def _execute_actions(
        self,
        actions: List[Dict[str, Any]],
        context: Dict[str, Any],
        organization_id: str,
        execution: Any
    ) -> List[Dict[str, Any]]:
        """Execute a list of actions sequentially"""
        results = []

        for index, action_config in enumerate(actions):
            try:
                execution.current_step = index + 1
                self.db.commit()

                # Create action instance
                action_type = action_config.get("type")
                action_class = self.ACTION_REGISTRY.get(action_type)

                if not action_class:
                    logger.warning(f"Unknown action type: {action_type}")
                    results.append({
                        "step": index + 1,
                        "action": action_type,
                        "success": False,
                        "error": f"Unknown action type: {action_type}"
                    })
                    continue

                action = action_class(action_config)

                # Execute action
                result = await action.execute(context, organization_id)

                # Update context with result
                if action_config.get("save_result_as"):
                    context[action_config["save_result_as"]] = result

                # Handle conditional branching
                if action_type == ActionType.CONDITION:
                    if result.get("condition_met"):
                        branch_results = await self._execute_actions(
                            result.get("true_branch", []),
                            context,
                            organization_id,
                            execution
                        )
                        results.extend(branch_results)
                    else:
                        branch_results = await self._execute_actions(
                            result.get("false_branch", []),
                            context,
                            organization_id,
                            execution
                        )
                        results.extend(branch_results)

                results.append({
                    "step": index + 1,
                    **result
                })

            except Exception as e:
                logger.error(f"Action {index + 1} failed: {e}")
                execution.error_step = index + 1
                execution.error_message = str(e)
                self.db.commit()

                results.append({
                    "step": index + 1,
                    "success": False,
                    "error": str(e)
                })

                # Stop on error unless configured to continue
                if not action_config.get("continue_on_error", False):
                    break

        return results

    async def test_workflow(
        self,
        workflow_config: Dict[str, Any],
        organization_id: str,
        test_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Test a workflow configuration without saving

        Args:
            workflow_config: Workflow configuration
            organization_id: Organization ID
            test_data: Test trigger data

        Returns:
            Test execution result
        """
        context = test_data or {}

        try:
            results = await self._execute_actions(
                workflow_config.get("actions", []),
                context,
                organization_id,
                None  # No execution record for tests
            )

            return {
                "success": True,
                "test": True,
                "results": results,
                "context": context
            }

        except Exception as e:
            logger.error(f"Workflow test failed: {e}")
            return {
                "success": False,
                "test": True,
                "error": str(e)
            }


# Singleton workflow engine instance
_workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine(db: Session) -> WorkflowEngine:
    """Get or create workflow engine instance"""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine(db)
    return _workflow_engine
