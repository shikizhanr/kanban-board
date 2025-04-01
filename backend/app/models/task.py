from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime
import enum


class TaskStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PLANNED)
    author_id = Column(Integer, ForeignKey('users.id'))

    # Отношения
    author = relationship("User", back_populates="created_tasks")
    assigned_users = relationship(
        "User",
        secondary="task_user_association",
        back_populates="assigned_tasks"
    )


task_user_association = Table(
    'task_user_association',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)