"""
BMAD v6 MCP Server CRUD Operations for Stories
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Story
from datetime import datetime

class CRUDStory:
    def create_story(
        self,
        db: Session,
        story_id: str,
        title: str,
        description: str,
        project_id: str,
        epic_id: str = None,
        acceptance_criteria: List[str] = None
    ) -> Story:
        """Create a new story."""
        db_story = Story(
            id=story_id,
            title=title,
            description=description,
            project_id=project_id,
            epic_id=epic_id,
            acceptance_criteria=acceptance_criteria or []
        )
        db.add(db_story)
        db.commit()
        db.refresh(db_story)
        return db_story
    
    def get_story(self, db: Session, story_id: str) -> Optional[Story]:
        """Get story by ID."""
        return db.query(Story).filter(Story.id == story_id).first()
    
    def get_stories_by_project(self, db: Session, project_id: str) -> List[Story]:
        """Get all stories for a project."""
        return db.query(Story).filter(Story.project_id == project_id).all()
    
    def get_stories_by_epic(self, db: Session, epic_id: str) -> List[Story]:
        """Get all stories for an epic."""
        return db.query(Story).filter(Story.epic_id == epic_id).all()
    
    def update_story_status(self, db: Session, story_id: str, status: str) -> Optional[Story]:
        """Update story status."""
        db_story = self.get_story(db, story_id)
        if db_story:
            db_story.status = status
            db_story.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_story)
        return db_story
    
    def update_story_state(self, db: Session, story_id: str, state: str) -> Optional[Story]:
        """Update story state."""
        db_story = self.get_story(db, story_id)
        if db_story:
            db_story.state = state
            db_story.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_story)
        return db_story
    
    def assign_story(self, db: Session, story_id: str, assignee: str) -> Optional[Story]:
        """Assign story to user."""
        db_story = self.get_story(db, story_id)
        if db_story:
            db_story.assignee = assignee
            db_story.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_story)
        return db_story
    
    def delete_story(self, db: Session, story_id: str) -> bool:
        """Delete story."""
        db_story = self.get_story(db, story_id)
        if db_story:
            db.delete(db_story)
            db.commit()
            return True
        return False

crud_story = CRUDStory()
