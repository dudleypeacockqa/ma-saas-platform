"""
BMAD v6 MCP Server WebSocket Endpoints
Real-time communication for live project updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, List, Any
import json
import asyncio
import logging
from datetime import datetime

from app.services.security_manager import SecurityManager
from app.services.state_manager import StateManager
from app.services.workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
security_manager = SecurityManager()
state_manager = StateManager()
workflow_engine = WorkflowEngine()

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.project_subscribers: Dict[str, List[WebSocket]] = {}
        self.workflow_subscribers: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection."""
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
        logger.info(f"WebSocket connected: {client_id}")
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        """Remove WebSocket connection."""
        if client_id in self.active_connections:
            if websocket in self.active_connections[client_id]:
                self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        
        # Remove from project subscriptions
        for project_id, connections in self.project_subscribers.items():
            if websocket in connections:
                connections.remove(websocket)
        
        # Remove from workflow subscriptions
        for workflow_name, connections in self.workflow_subscribers.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_personal_message(self, message: str, client_id: str):
        """Send message to specific client."""
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Connection is broken, will be cleaned up on disconnect
                    pass
    
    async def broadcast_to_project(self, message: str, project_id: str):
        """Broadcast message to all subscribers of a project."""
        if project_id in self.project_subscribers:
            for connection in self.project_subscribers[project_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Connection is broken, will be cleaned up on disconnect
                    pass
    
    async def broadcast_to_workflow(self, message: str, workflow_name: str):
        """Broadcast message to all subscribers of a workflow."""
        if workflow_name in self.workflow_subscribers:
            for connection in self.workflow_subscribers[workflow_name]:
                try:
                    await connection.send_text(message)
                except:
                    # Connection is broken, will be cleaned up on disconnect
                    pass
    
    def subscribe_to_project(self, websocket: WebSocket, project_id: str):
        """Subscribe WebSocket to project updates."""
        if project_id not in self.project_subscribers:
            self.project_subscribers[project_id] = []
        if websocket not in self.project_subscribers[project_id]:
            self.project_subscribers[project_id].append(websocket)
        logger.info(f"Subscribed to project: {project_id}")
    
    def subscribe_to_workflow(self, websocket: WebSocket, workflow_name: str):
        """Subscribe WebSocket to workflow updates."""
        if workflow_name not in self.workflow_subscribers:
            self.workflow_subscribers[workflow_name] = []
        if websocket not in self.workflow_subscribers[workflow_name]:
            self.workflow_subscribers[workflow_name].append(websocket)
        logger.info(f"Subscribed to workflow: {workflow_name}")

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint for real-time communication."""
    await manager.connect(websocket, client_id)
    
    try:
        # Send welcome message
        welcome_message = {
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "bmad_version": "6.0.0"
        }
        await websocket.send_text(json.dumps(welcome_message))
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            await handle_websocket_message(websocket, client_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {str(e)}")
        manager.disconnect(websocket, client_id)

async def handle_websocket_message(websocket: WebSocket, client_id: str, message: Dict[str, Any]):
    """Handle incoming WebSocket messages."""
    try:
        message_type = message.get("type")
        
        if message_type == "subscribe_project":
            project_id = message.get("project_id")
            if project_id:
                manager.subscribe_to_project(websocket, project_id)
                await send_project_status(websocket, project_id)
        
        elif message_type == "subscribe_workflow":
            workflow_name = message.get("workflow_name")
            if workflow_name:
                manager.subscribe_to_workflow(websocket, workflow_name)
        
        elif message_type == "get_project_status":
            project_id = message.get("project_id")
            if project_id:
                await send_project_status(websocket, project_id)
        
        elif message_type == "execute_workflow":
            await handle_workflow_execution(websocket, client_id, message)
        
        elif message_type == "ping":
            pong_message = {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_text(json.dumps(pong_message))
        
        else:
            error_message = {
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_text(json.dumps(error_message))
    
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {str(e)}")
        error_message = {
            "type": "error",
            "message": "Failed to process message",
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(error_message))

async def send_project_status(websocket: WebSocket, project_id: str):
    """Send current project status to WebSocket."""
    try:
        project_state = await state_manager.get_project_state(project_id)
        
        if project_state:
            status_message = {
                "type": "project_status",
                "project_id": project_id,
                "current_phase": project_state.current_phase.value,
                "scale_level": project_state.scale_level.value,
                "backlog_count": len(project_state.backlog),
                "todo": project_state.todo,
                "in_progress": project_state.in_progress,
                "done_count": len(project_state.done),
                "last_updated": project_state.last_updated.isoformat(),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            status_message = {
                "type": "project_status",
                "project_id": project_id,
                "status": "not_found",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        await websocket.send_text(json.dumps(status_message))
    
    except Exception as e:
        logger.error(f"Error sending project status: {str(e)}")

async def handle_workflow_execution(websocket: WebSocket, client_id: str, message: Dict[str, Any]):
    """Handle workflow execution request via WebSocket."""
    try:
        workflow_name = message.get("workflow_name")
        project_id = message.get("project_id")
        context = message.get("context", {})
        
        if not workflow_name or not project_id:
            error_message = {
                "type": "workflow_error",
                "message": "Missing workflow_name or project_id",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_text(json.dumps(error_message))
            return
        
        # Send workflow started message
        started_message = {
            "type": "workflow_started",
            "workflow_name": workflow_name,
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(started_message))
        
        # Execute workflow
        result = await workflow_engine.execute_workflow(
            workflow_name=workflow_name,
            context=context,
            project_id=project_id
        )
        
        # Send workflow completed message
        completed_message = {
            "type": "workflow_completed",
            "workflow_name": workflow_name,
            "project_id": project_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(completed_message))
        
        # Broadcast to other subscribers
        await manager.broadcast_to_project(json.dumps(completed_message), project_id)
        await manager.broadcast_to_workflow(json.dumps(completed_message), workflow_name)
    
    except Exception as e:
        logger.error(f"Error executing workflow via WebSocket: {str(e)}")
        error_message = {
            "type": "workflow_error",
            "workflow_name": workflow_name,
            "project_id": project_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(error_message))

# Utility functions for broadcasting updates

async def broadcast_project_update(project_id: str, update_type: str, data: Dict[str, Any]):
    """Broadcast project update to all subscribers."""
    message = {
        "type": "project_update",
        "project_id": project_id,
        "update_type": update_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_project(json.dumps(message), project_id)

async def broadcast_workflow_update(workflow_name: str, update_type: str, data: Dict[str, Any]):
    """Broadcast workflow update to all subscribers."""
    message = {
        "type": "workflow_update",
        "workflow_name": workflow_name,
        "update_type": update_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_workflow(json.dumps(message), workflow_name)

async def broadcast_story_update(project_id: str, story_id: str, update_type: str, data: Dict[str, Any]):
    """Broadcast story update to project subscribers."""
    message = {
        "type": "story_update",
        "project_id": project_id,
        "story_id": story_id,
        "update_type": update_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_project(json.dumps(message), project_id)

async def broadcast_deal_update(project_id: str, deal_id: str, update_type: str, data: Dict[str, Any]):
    """Broadcast M&A deal update to project subscribers."""
    message = {
        "type": "deal_update",
        "project_id": project_id,
        "deal_id": deal_id,
        "update_type": update_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_project(json.dumps(message), project_id)

# Health check for WebSocket connections
async def websocket_health_check():
    """Periodic health check for WebSocket connections."""
    while True:
        try:
            # Send ping to all active connections
            ping_message = {
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for client_id, connections in manager.active_connections.items():
                for connection in connections[:]:  # Create copy to avoid modification during iteration
                    try:
                        await connection.send_text(json.dumps(ping_message))
                    except:
                        # Connection is broken, remove it
                        manager.disconnect(connection, client_id)
            
            # Wait 30 seconds before next health check
            await asyncio.sleep(30)
        
        except Exception as e:
            logger.error(f"WebSocket health check error: {str(e)}")
            await asyncio.sleep(30)

# Start health check task when module is imported
asyncio.create_task(websocket_health_check())
