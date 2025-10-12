"""
Automation Engine
AI-driven workflow automation and intelligent notifications
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
from .ai_service import AIService, AIRequest, AIResponse, AITask, AIModel, get_ai_service

class TriggerType(str, Enum):
    """Types of automation triggers"""
    DEAL_STAGE_CHANGE = "deal_stage_change"
    DOCUMENT_UPLOADED = "document_uploaded"
    DEADLINE_APPROACHING = "deadline_approaching"
    SCORE_THRESHOLD = "score_threshold"
    USER_ACTION = "user_action"
    TIME_BASED = "time_based"
    DATA_ANOMALY = "data_anomaly"
    EXTERNAL_EVENT = "external_event"

class ActionType(str, Enum):
    """Types of automated actions"""
    SEND_NOTIFICATION = "send_notification"
    UPDATE_DEAL_STAGE = "update_deal_stage"
    ASSIGN_TASK = "assign_task"
    GENERATE_REPORT = "generate_report"
    SCHEDULE_MEETING = "schedule_meeting"
    CREATE_DOCUMENT = "create_document"
    SEND_EMAIL = "send_email"
    UPDATE_STATUS = "update_status"
    ESCALATE_ISSUE = "escalate_issue"
    TRIGGER_ANALYSIS = "trigger_analysis"

class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

@dataclass
class WorkflowTrigger:
    """Workflow automation trigger configuration"""
    trigger_id: str
    name: str
    trigger_type: TriggerType
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    is_active: bool
    organization_id: str
    created_by: str
    created_at: datetime
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
@dataclass
class SmartNotification:
    """AI-enhanced smart notification"""
    notification_id: str
    title: str
    message: str
    priority: NotificationPriority
    notification_type: str
    target_users: List[str]
    context_data: Dict[str, Any]
    suggested_actions: List[Dict[str, Any]]
    ai_insights: Optional[str] = None
    delivery_channels: List[str] = None
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    
@dataclass
class AutomationResult:
    """Result of automation execution"""
    automation_id: str
    trigger_id: str
    success: bool
    actions_executed: List[str]
    notifications_sent: List[str]
    errors: List[str]
    execution_time_ms: int
    timestamp: datetime
    context: Dict[str, Any]
    
class AutomationEngine:
    """AI-driven workflow automation engine"""
    
    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or get_ai_service()
        self.active_triggers: Dict[str, WorkflowTrigger] = {}
        self.notification_templates = self._initialize_notification_templates()
        self.automation_history: List[AutomationResult] = []
        self.running = False
        
    def _initialize_notification_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize smart notification templates"""
        return {
            "deal_score_high": {
                "title": "High-Value Deal Opportunity Identified",
                "template": "Deal '{deal_title}' has received a high score of {score}/100. AI analysis suggests immediate attention.",
                "priority": NotificationPriority.HIGH,
                "suggested_actions": [
                    {"action": "Schedule due diligence", "type": "schedule"},
                    {"action": "Review AI insights", "type": "view"},
                    {"action": "Contact stakeholders", "type": "communication"}
                ]
            },
            "deal_risk_detected": {
                "title": "Risk Factors Detected in Deal",
                "template": "AI analysis has identified potential risks in deal '{deal_title}': {risk_summary}",
                "priority": NotificationPriority.MEDIUM,
                "suggested_actions": [
                    {"action": "Review risk assessment", "type": "view"},
                    {"action": "Request additional documentation", "type": "request"},
                    {"action": "Consult risk team", "type": "escalate"}
                ]
            },
            "document_analyzed": {
                "title": "Document Analysis Complete",
                "template": "AI analysis of '{document_name}' is complete. Key insights: {key_insights}",
                "priority": NotificationPriority.MEDIUM,
                "suggested_actions": [
                    {"action": "View analysis report", "type": "view"},
                    {"action": "Share with team", "type": "share"},
                    {"action": "Update deal notes", "type": "update"}
                ]
            },
            "deadline_approaching": {
                "title": "Important Deadline Approaching",
                "template": "The deadline for '{task_name}' is approaching ({days_remaining} days remaining).",
                "priority": NotificationPriority.HIGH,
                "suggested_actions": [
                    {"action": "Review progress", "type": "view"},
                    {"action": "Update timeline", "type": "update"},
                    {"action": "Notify stakeholders", "type": "communication"}
                ]
            },
            "market_insight": {
                "title": "New Market Intelligence Available",
                "template": "AI has identified new market trends in {industry}: {insight_summary}",
                "priority": NotificationPriority.LOW,
                "suggested_actions": [
                    {"action": "View full report", "type": "view"},
                    {"action": "Update strategy", "type": "update"},
                    {"action": "Share insights", "type": "share"}
                ]
            }
        }
    
    async def register_trigger(self, trigger: WorkflowTrigger) -> bool:
        """Register a new workflow trigger"""
        try:
            self.active_triggers[trigger.trigger_id] = trigger
            return True
        except Exception as e:
            print(f"Error registering trigger {trigger.trigger_id}: {e}")
            return False
    
    async def process_event(self, event_type: str, event_data: Dict[str, Any]) -> List[AutomationResult]:
        """Process an event and execute matching automation triggers"""
        results = []
        
        for trigger_id, trigger in self.active_triggers.items():
            if not trigger.is_active:
                continue
                
            # Check if event matches trigger conditions
            if await self._evaluate_trigger_conditions(trigger, event_type, event_data):
                result = await self._execute_trigger(trigger, event_data)
                results.append(result)
                
                # Update trigger statistics
                trigger.last_triggered = datetime.now()
                trigger.trigger_count += 1
        
        return results
    
    async def _evaluate_trigger_conditions(self, trigger: WorkflowTrigger, 
                                         event_type: str, event_data: Dict[str, Any]) -> bool:
        """Evaluate if trigger conditions are met"""
        conditions = trigger.conditions
        
        # Check trigger type match
        if trigger.trigger_type.value != event_type:
            return False
        
        # Evaluate conditions using AI
        if conditions.get("use_ai_evaluation", False):
            ai_request = AIRequest(
                task=AITask.CLASSIFY_CONTENT,
                model=AIModel.RECOMMENDATION_ENGINE,
                input_data={
                    "event_data": event_data,
                    "conditions": conditions,
                    "evaluation_type": "trigger_conditions"
                }
            )
            
            ai_response = await self.ai_service.process_request(ai_request)
            return ai_response.result.get("should_trigger", False)
        
        # Simple condition evaluation
        for condition_key, condition_value in conditions.items():
            if condition_key == "use_ai_evaluation":
                continue
                
            event_value = event_data.get(condition_key)
            
            if isinstance(condition_value, dict):
                operator = condition_value.get("operator", "equals")
                target_value = condition_value.get("value")
                
                if operator == "equals" and event_value != target_value:
                    return False
                elif operator == "greater_than" and (event_value or 0) <= target_value:
                    return False
                elif operator == "less_than" and (event_value or 0) >= target_value:
                    return False
                elif operator == "contains" and target_value not in str(event_value or ""):
                    return False
            else:
                if event_value != condition_value:
                    return False
        
        return True
    
    async def _execute_trigger(self, trigger: WorkflowTrigger, event_data: Dict[str, Any]) -> AutomationResult:
        """Execute actions for a triggered workflow"""
        start_time = datetime.now()
        automation_id = f"auto_{trigger.trigger_id}_{int(start_time.timestamp())}"
        
        actions_executed = []
        notifications_sent = []
        errors = []
        
        for action in trigger.actions:
            try:
                action_type = ActionType(action.get("type"))
                action_result = await self._execute_action(action_type, action, event_data)
                
                if action_result.get("success", False):
                    actions_executed.append(action_type.value)
                    if action_type == ActionType.SEND_NOTIFICATION:
                        notifications_sent.append(action_result.get("notification_id", ""))
                else:
                    errors.append(action_result.get("error", "Unknown error"))
                    
            except Exception as e:
                errors.append(f"Action execution failed: {str(e)}")
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        result = AutomationResult(
            automation_id=automation_id,
            trigger_id=trigger.trigger_id,
            success=len(errors) == 0,
            actions_executed=actions_executed,
            notifications_sent=notifications_sent,
            errors=errors,
            execution_time_ms=execution_time,
            timestamp=datetime.now(),
            context=event_data
        )
        
        self.automation_history.append(result)
        return result
    
    async def _execute_action(self, action_type: ActionType, action_config: Dict[str, Any], 
                            event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific automation action"""
        try:
            if action_type == ActionType.SEND_NOTIFICATION:
                return await self._send_smart_notification(action_config, event_data)
            
            elif action_type == ActionType.UPDATE_DEAL_STAGE:
                return await self._update_deal_stage(action_config, event_data)
            
            elif action_type == ActionType.ASSIGN_TASK:
                return await self._assign_task(action_config, event_data)
            
            elif action_type == ActionType.GENERATE_REPORT:
                return await self._generate_automated_report(action_config, event_data)
            
            elif action_type == ActionType.TRIGGER_ANALYSIS:
                return await self._trigger_ai_analysis(action_config, event_data)
            
            else:
                return {"success": False, "error": f"Unsupported action type: {action_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_smart_notification(self, action_config: Dict[str, Any], 
                                     event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an AI-enhanced smart notification"""
        template_name = action_config.get("template", "generic")
        template = self.notification_templates.get(template_name, {})
        
        # Use AI to enhance notification content
        ai_request = AIRequest(
            task=AITask.GENERATE_INSIGHTS,
            model=AIModel.CONTENT_SUMMARIZER,
            input_data={
                "event_data": event_data,
                "template": template,
                "personalization_context": action_config.get("context", {})
            }
        )
        
        ai_response = await self.ai_service.process_request(ai_request)
        
        # Create enhanced notification
        notification = SmartNotification(
            notification_id=f"notif_{int(datetime.now().timestamp())}",
            title=template.get("title", "Automated Notification"),
            message=self._format_notification_message(template, event_data),
            priority=NotificationPriority(template.get("priority", NotificationPriority.MEDIUM)),
            notification_type=action_config.get("type", "automation"),
            target_users=action_config.get("target_users", []),
            context_data=event_data,
            suggested_actions=template.get("suggested_actions", []),
            ai_insights=ai_response.result.get("insights", ""),
            delivery_channels=action_config.get("channels", ["web"]),
            created_at=datetime.now()
        )
        
        # In a real implementation, this would send the notification
        # For now, we'll just log it
        print(f"Smart notification sent: {notification.title}")
        
        return {
            "success": True,
            "notification_id": notification.notification_id,
            "message": "Notification sent successfully"
        }
    
    async def _update_deal_stage(self, action_config: Dict[str, Any], 
                               event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update deal stage automatically"""
        deal_id = event_data.get("deal_id")
        new_stage = action_config.get("new_stage")
        
        if not deal_id or not new_stage:
            return {"success": False, "error": "Missing deal_id or new_stage"}
        
        # In a real implementation, this would update the database
        print(f"Deal {deal_id} stage updated to {new_stage}")
        
        return {
            "success": True,
            "deal_id": deal_id,
            "new_stage": new_stage,
            "message": "Deal stage updated successfully"
        }
    
    async def _assign_task(self, action_config: Dict[str, Any], 
                         event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a task automatically"""
        assignee = action_config.get("assignee")
        task_type = action_config.get("task_type")
        
        # Use AI to generate task description
        ai_request = AIRequest(
            task=AITask.GENERATE_INSIGHTS,
            model=AIModel.RECOMMENDATION_ENGINE,
            input_data={
                "event_data": event_data,
                "task_type": task_type,
                "context": "task_generation"
            }
        )
        
        ai_response = await self.ai_service.process_request(ai_request)
        
        task_description = ai_response.result.get("task_description", f"Complete {task_type}")
        
        # In a real implementation, this would create a task in the system
        print(f"Task assigned to {assignee}: {task_description}")
        
        return {
            "success": True,
            "assignee": assignee,
            "task_description": task_description,
            "message": "Task assigned successfully"
        }
    
    async def _generate_automated_report(self, action_config: Dict[str, Any], 
                                       event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an automated report"""
        report_type = action_config.get("report_type", "summary")
        
        # Use AI to generate report content
        ai_request = AIRequest(
            task=AITask.GENERATE_INSIGHTS,
            model=AIModel.MARKET_INTELLIGENCE,
            input_data={
                "event_data": event_data,
                "report_type": report_type,
                "analysis_context": "automated_reporting"
            }
        )
        
        ai_response = await self.ai_service.process_request(ai_request)
        
        report_content = ai_response.result.get("report_content", "Report generated")
        
        # In a real implementation, this would save the report
        print(f"Automated report generated: {report_type}")
        
        return {
            "success": True,
            "report_type": report_type,
            "content_length": len(report_content),
            "message": "Report generated successfully"
        }
    
    async def _trigger_ai_analysis(self, action_config: Dict[str, Any], 
                                 event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger additional AI analysis"""
        analysis_type = action_config.get("analysis_type", "general")
        
        # Determine appropriate AI task and model
        task_mapping = {
            "document": (AITask.ANALYZE_DOCUMENT, AIModel.DOCUMENT_ANALYZER),
            "deal_scoring": (AITask.SCORE_DEAL, AIModel.DEAL_SCORER),
            "market_intelligence": (AITask.GENERATE_INSIGHTS, AIModel.MARKET_INTELLIGENCE),
            "risk_assessment": (AITask.DETECT_ANOMALIES, AIModel.RISK_ASSESSOR)
        }
        
        task, model = task_mapping.get(analysis_type, (AITask.GENERATE_INSIGHTS, AIModel.MARKET_INTELLIGENCE))
        
        ai_request = AIRequest(
            task=task,
            model=model,
            input_data=event_data
        )
        
        ai_response = await self.ai_service.process_request(ai_request)
        
        return {
            "success": True,
            "analysis_type": analysis_type,
            "confidence": ai_response.confidence,
            "message": "AI analysis triggered successfully"
        }
    
    def _format_notification_message(self, template: Dict[str, Any], 
                                   event_data: Dict[str, Any]) -> str:
        """Format notification message with event data"""
        message_template = template.get("template", "Event occurred: {event_type}")
        
        try:
            return message_template.format(**event_data)
        except KeyError:
            # If template variables are missing, return a generic message
            return f"Automated notification: {event_data.get('event_type', 'Unknown event')}"
    
    def get_active_triggers(self) -> List[WorkflowTrigger]:
        """Get list of active triggers"""
        return [trigger for trigger in self.active_triggers.values() if trigger.is_active]
    
    def get_automation_history(self, limit: int = 50) -> List[AutomationResult]:
        """Get recent automation history"""
        return sorted(self.automation_history, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_automation_stats(self) -> Dict[str, Any]:
        """Get automation engine statistics"""
        total_automations = len(self.automation_history)
        successful_automations = sum(1 for result in self.automation_history if result.success)
        
        return {
            "active_triggers": len([t for t in self.active_triggers.values() if t.is_active]),
            "total_triggers": len(self.active_triggers),
            "total_automations_executed": total_automations,
            "successful_automations": successful_automations,
            "success_rate": (successful_automations / max(total_automations, 1)) * 100,
            "notification_templates": len(self.notification_templates),
            "engine_status": "active" if self.running else "stopped"
        }
    
    async def start_engine(self):
        """Start the automation engine"""
        self.running = True
        print("Automation engine started")
    
    async def stop_engine(self):
        """Stop the automation engine"""
        self.running = False
        print("Automation engine stopped")

# Global automation engine
_automation_engine: Optional[AutomationEngine] = None

def get_automation_engine() -> AutomationEngine:
    """Get global automation engine instance"""
    global _automation_engine
    if _automation_engine is None:
        _automation_engine = AutomationEngine()
    return _automation_engine