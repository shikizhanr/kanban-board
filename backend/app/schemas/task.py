from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum


class TaskStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.PLANNED
    assigned_user_ids: Optional[List[int]] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int
    date: datetime
    author_id: int
    assigned_users: List[dict]  # Добавляем информацию о назначенных пользователях

    class Config:
        from_attributes = True
