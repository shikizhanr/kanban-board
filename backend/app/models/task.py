from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime
import enum


class TaskStatus(str, enum.Enum):
    PLANNED = "Запланировано"
    IN_PROGRESS = "В работе"
    COMPLETED = "Готово"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))

    created_tasks = relationship("Task", back_populates="author")
    assigned_tasks = relationship(
        "Task",
        secondary="task_user_association",
        back_populates="assigned_users",
        overlaps="assigned_tasks"
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)
    task_type = Column(String(50))
    status = Column(Enum(TaskStatus), default=TaskStatus.PLANNED)
    author_id = Column(Integer, ForeignKey("users.id"))

    author = relationship("User", back_populates="created_tasks")
    assigned_users = relationship(
        "User",
        secondary="task_user_association",
        back_populates="assigned_tasks",
        overlaps="assigned_users"
    )


task_user_association = Table(
    "task_user_association",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id")),
    Column("user_id", Integer, ForeignKey("users.id"))
)