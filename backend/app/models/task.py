from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from app.db.session import Base
# Убедимся, что User импортирован, если он нужен для связей
from app.models.user import User
import enum

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
    # ИСПРАВЛЕНО: Возвращаем tablename, чтобы SQLAlchemy знала имя таблицы
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.todo)
    type = Column(Enum(TaskType), default=TaskType.development)
    time_spent = Column(Float, default=0.0)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    creator = relationship("User", foreign_keys=[creator_id], backref="created_tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], backref="assigned_tasks")