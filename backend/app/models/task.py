from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Float, Table
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.user import User
import enum

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
    status = Column(Enum(TaskStatus), default=TaskStatus.todo)
    type = Column(Enum(TaskType), default=TaskType.development)
    time_spent = Column(Float, default=0.0)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # УДАЛЕНО: assignee_id больше не нужен
    # assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", foreign_keys=[creator_id], backref="created_tasks")
    assignees = relationship(
        "User", secondary=task_assignees_table, backref="assigned_tasks"
    )