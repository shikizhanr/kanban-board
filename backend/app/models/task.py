from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime # Make sure datetime is imported from datetime
import enum

# It's good practice to import func from sqlalchemy for database functions like now()
from sqlalchemy.sql import func


class TaskStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskProfile(str, enum.Enum): # Added for task_profile
    DEVELOPMENT = "development"
    ANALYTICS = "analytics"
    DOCUMENTATION = "documentation"
    GENERAL = "general"


class Task(Base):
    tablename = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False) # Assuming title should not be nullable
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PLANNED, nullable=False)
    
    # New fields
    task_profile = Column(Enum(TaskProfile), default=TaskProfile.GENERAL, nullable=False)
    time_spent = Column(Integer, default=0, nullable=False) # In minutes or defined unit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    author = relationship("User", back_populates="created_tasks")
    assigned_users = relationship(
        "User",
        secondary="task_user_association",
        back_populates="assigned_tasks"
    )


task_user_association = Table(
    'task_user_association',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True), # Added primary_key=True for association table best practice
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)  # Added primary_key=True
)