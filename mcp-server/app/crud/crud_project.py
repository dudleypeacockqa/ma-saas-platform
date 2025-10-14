"""
BMAD v6 MCP Server CRUD Operations for Projects
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Project, Story, Epic
from app.models.bmad_models import ProjectState, ScaleLevel, ProjectPhase
from datetime import datetime

class CRUDProject:
    def create_project(
        self, 
        db: Session, 
        project_id: str, 
        name: str, 
        description: str = None,
        phase: int = 1,
        scale_level: int = 1
    ) -> Project:
        """Create a new project."""
        db_project = Project(
            id=project_id,
            name=name,
            description=description,
            current_phase=phase,
            scale_level=scale_level
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    def get_project(self, db: Session, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        return db.query(Project).filter(Project.id == project_id).first()
    
    def get_projects(self, db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get list of projects."""
        return db.query(Project).offset(skip).limit(limit).all()
    
    def update_project_phase(self, db: Session, project_id: str, new_phase: int) -> Optional[Project]:
        """Update project phase."""
        db_project = self.get_project(db, project_id)
        if db_project:
            db_project.current_phase = new_phase
            db_project.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_project)
        return db_project
    
    def update_project_state(
        self, 
        db: Session, 
        project_id: str, 
        backlog: List[str] = None,
        todo: str = None,
        in_progress: str = None,
        done: List[str] = None
    ) -> Optional[Project]:
        """Update project state machine."""
        db_project = self.get_project(db, project_id)
        if db_project:
            if backlog is not None:
                db_project.backlog = backlog
            if todo is not None:
                db_project.todo = todo
            if in_progress is not None:
                db_project.in_progress = in_progress
            if done is not None:
                db_project.done = done
            
            db_project.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_project)
        return db_project
    
    def delete_project(self, db: Session, project_id: str) -> bool:
        """Delete project."""
        db_project = self.get_project(db, project_id)
        if db_project:
            db.delete(db_project)
            db.commit()
            return True
        return False

crud_project = CRUDProject()
