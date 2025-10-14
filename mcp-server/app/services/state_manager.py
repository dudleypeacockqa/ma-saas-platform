"""
BMAD v6 State Manager Service
Manages project state persistence and BMAD v6 state machine operations
"""

import json
import asyncio
from typing import Dict, Optional, List, Any
from datetime import datetime
import logging

from app.models.bmad_models import ProjectState, ProjectPhase, ScaleLevel, StoryState

logger = logging.getLogger(__name__)

class StateManager:
    """Manages BMAD v6 project states and workflow persistence."""
    
    def __init__(self):
        self.project_states: Dict[str, ProjectState] = {}
        self.state_history: Dict[str, List[Dict[str, Any]]] = {}
        
        logger.info("Initialized BMAD v6 State Manager")
    
    async def create_project_state(
        self, 
        project_id: str, 
        phase: ProjectPhase, 
        scale_level: ScaleLevel
    ) -> ProjectState:
        """Create new project state."""
        
        project_state = ProjectState(
            project_id=project_id,
            current_phase=phase,
            scale_level=scale_level
        )
        
        self.project_states[project_id] = project_state
        await self._record_state_change(project_id, "project_created", {
            "phase": phase.value,
            "scale_level": scale_level.value
        })
        
        logger.info(f"Created project state: {project_id}")
        return project_state
    
    async def get_project_state(self, project_id: str) -> Optional[ProjectState]:
        """Get current project state."""
        return self.project_states.get(project_id)
    
    async def update_project_phase(self, project_id: str, new_phase: ProjectPhase) -> bool:
        """Update project phase."""
        try:
            project_state = self.project_states.get(project_id)
            if not project_state:
                logger.error(f"Project state not found: {project_id}")
                return False
            
            old_phase = project_state.current_phase
            project_state.current_phase = new_phase
            project_state.last_updated = datetime.utcnow()
            
            await self._record_state_change(project_id, "phase_transition", {
                "from_phase": old_phase.value,
                "to_phase": new_phase.value
            })
            
            logger.info(f"Updated project phase: {project_id} -> {new_phase.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update project phase: {str(e)}")
            return False
    
    async def transition_story_state(
        self, 
        project_id: str, 
        story_id: str, 
        from_state: StoryState, 
        to_state: StoryState
    ) -> bool:
        """Transition story through BMAD v6 state machine."""
        try:
            project_state = self.project_states.get(project_id)
            if not project_state:
                logger.error(f"Project state not found: {project_id}")
                return False
            
            # Validate and execute state transition
            success = await self._execute_story_transition(
                project_state, story_id, from_state, to_state
            )
            
            if success:
                project_state.last_updated = datetime.utcnow()
                await self._record_state_change(project_id, "story_transition", {
                    "story_id": story_id,
                    "from_state": from_state.value,
                    "to_state": to_state.value
                })
                
                logger.info(f"Story transition: {story_id} {from_state.value} -> {to_state.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Story transition failed: {str(e)}")
            return False
    
    async def _execute_story_transition(
        self, 
        project_state: ProjectState, 
        story_id: str, 
        from_state: StoryState, 
        to_state: StoryState
    ) -> bool:
        """Execute story state transition following BMAD v6 state machine."""
        
        # BACKLOG -> TODO
        if from_state == StoryState.BACKLOG and to_state == StoryState.TODO:
            if story_id in project_state.backlog:
                project_state.backlog.remove(story_id)
                project_state.todo = story_id
                return True
        
        # TODO -> IN_PROGRESS
        elif from_state == StoryState.TODO and to_state == StoryState.IN_PROGRESS:
            if project_state.todo == story_id:
                project_state.in_progress = story_id
                # Move next story from backlog to todo
                if project_state.backlog:
                    project_state.todo = project_state.backlog.pop(0)
                else:
                    project_state.todo = None
                return True
        
        # IN_PROGRESS -> DONE
        elif from_state == StoryState.IN_PROGRESS and to_state == StoryState.DONE:
            if project_state.in_progress == story_id:
                # Add to done with timestamp
                done_entry = f"{story_id}:{datetime.utcnow().isoformat()}"
                project_state.done.append(done_entry)
                
                # Move next story if available
                if project_state.todo:
                    project_state.in_progress = project_state.todo
                    if project_state.backlog:
                        project_state.todo = project_state.backlog.pop(0)
                    else:
                        project_state.todo = None
                else:
                    project_state.in_progress = None
                
                return True
        
        logger.warning(f"Invalid story transition: {story_id} {from_state.value} -> {to_state.value}")
        return False
    
    async def populate_backlog(self, project_id: str, story_ids: List[str]) -> bool:
        """Populate project backlog with story IDs."""
        try:
            project_state = self.project_states.get(project_id)
            if not project_state:
                logger.error(f"Project state not found: {project_id}")
                return False
            
            project_state.backlog = story_ids.copy()
            
            # Move first story to TODO if backlog not empty
            if project_state.backlog and not project_state.todo:
                project_state.todo = project_state.backlog.pop(0)
            
            project_state.last_updated = datetime.utcnow()
            
            await self._record_state_change(project_id, "backlog_populated", {
                "story_count": len(story_ids),
                "story_ids": story_ids
            })
            
            logger.info(f"Populated backlog for project {project_id} with {len(story_ids)} stories")
            return True
            
        except Exception as e:
            logger.error(f"Failed to populate backlog: {str(e)}")
            return False
    
    async def get_next_story(self, project_id: str) -> Optional[str]:
        """Get next story to work on (from TODO state)."""
        project_state = self.project_states.get(project_id)
        if not project_state:
            return None
        
        return project_state.todo
    
    async def get_current_story(self, project_id: str) -> Optional[str]:
        """Get currently active story (from IN_PROGRESS state)."""
        project_state = self.project_states.get(project_id)
        if not project_state:
            return None
        
        return project_state.in_progress
    
    async def get_project_progress(self, project_id: str) -> Dict[str, Any]:
        """Get project progress statistics."""
        project_state = self.project_states.get(project_id)
        if not project_state:
            return {}
        
        total_stories = (
            len(project_state.backlog) + 
            (1 if project_state.todo else 0) +
            (1 if project_state.in_progress else 0) +
            len(project_state.done)
        )
        
        completed_stories = len(project_state.done)
        
        progress_percentage = (completed_stories / total_stories * 100) if total_stories > 0 else 0
        
        return {
            "project_id": project_id,
            "total_stories": total_stories,
            "completed_stories": completed_stories,
            "progress_percentage": round(progress_percentage, 2),
            "current_phase": project_state.current_phase.value,
            "scale_level": project_state.scale_level.value,
            "state_breakdown": {
                "backlog": len(project_state.backlog),
                "todo": 1 if project_state.todo else 0,
                "in_progress": 1 if project_state.in_progress else 0,
                "done": len(project_state.done)
            }
        }
    
    async def _record_state_change(self, project_id: str, action: str, details: Dict[str, Any]):
        """Record state change in history for audit and debugging."""
        if project_id not in self.state_history:
            self.state_history[project_id] = []
        
        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "details": details
        }
        
        self.state_history[project_id].append(history_entry)
        
        # Keep only last 100 entries per project
        if len(self.state_history[project_id]) > 100:
            self.state_history[project_id] = self.state_history[project_id][-100:]
    
    async def get_state_history(self, project_id: str) -> List[Dict[str, Any]]:
        """Get state change history for project."""
        return self.state_history.get(project_id, [])
    
    async def export_project_state(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Export complete project state for backup or transfer."""
        project_state = self.project_states.get(project_id)
        if not project_state:
            return None
        
        return {
            "project_state": {
                "project_id": project_state.project_id,
                "current_phase": project_state.current_phase.value,
                "scale_level": project_state.scale_level.value,
                "backlog": project_state.backlog,
                "todo": project_state.todo,
                "in_progress": project_state.in_progress,
                "done": project_state.done,
                "created_at": project_state.created_at.isoformat(),
                "last_updated": project_state.last_updated.isoformat()
            },
            "state_history": self.state_history.get(project_id, []),
            "export_timestamp": datetime.utcnow().isoformat()
        }
    
    async def import_project_state(self, state_data: Dict[str, Any]) -> bool:
        """Import project state from backup or transfer."""
        try:
            project_data = state_data["project_state"]
            project_id = project_data["project_id"]
            
            # Recreate project state
            project_state = ProjectState(
                project_id=project_id,
                current_phase=ProjectPhase(project_data["current_phase"]),
                scale_level=ScaleLevel(project_data["scale_level"]),
                backlog=project_data["backlog"],
                todo=project_data["todo"],
                in_progress=project_data["in_progress"],
                done=project_data["done"],
                created_at=datetime.fromisoformat(project_data["created_at"]),
                last_updated=datetime.fromisoformat(project_data["last_updated"])
            )
            
            self.project_states[project_id] = project_state
            
            # Import history if available
            if "state_history" in state_data:
                self.state_history[project_id] = state_data["state_history"]
            
            logger.info(f"Imported project state: {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import project state: {str(e)}")
            return False
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Get state manager statistics."""
        total_stories = 0
        phase_counts = {}
        scale_counts = {}
        
        for project_state in self.project_states.values():
            # Count stories
            total_stories += (
                len(project_state.backlog) + 
                (1 if project_state.todo else 0) +
                (1 if project_state.in_progress else 0) +
                len(project_state.done)
            )
            
            # Count phases
            phase = project_state.current_phase.value
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
            
            # Count scale levels
            scale = project_state.scale_level.value
            scale_counts[scale] = scale_counts.get(scale, 0) + 1
        
        return {
            "total_projects": len(self.project_states),
            "total_stories": total_stories,
            "projects_by_phase": phase_counts,
            "projects_by_scale": scale_counts,
            "total_history_entries": sum(len(h) for h in self.state_history.values())
        }
