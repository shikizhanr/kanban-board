from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemyEnum, Float, Table, DateTime # Added DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.user import User
import enum
from datetime import datetime # Added datetime import

task_assignees_table = Table(
    "task_assignees",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class TaskType(str, enum.Enum):
    development = "development"
    analytics = "analytics"
    documentation = "documentation"
    testing = "testing"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(SQLAlchemyEnum(TaskStatus), default=TaskStatus.todo) # Use SQLAlchemyEnum
    type = Column(SQLAlchemyEnum(TaskType), default=TaskType.development) # Use SQLAlchemyEnum
    priority = Column(String, default='medium', nullable=False, index=True) # Added priority field
    time_spent = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False) # Added created_at field

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    creator = relationship("User", foreign_keys=[creator_id], backref="created_tasks")
    
    assignees = relationship(
        "User", secondary=task_assignees_table, backref="assigned_tasks"
    )
