from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum


class TaskStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class UserBase(BaseModel):
    first_name: str
    last_name: str


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


class UserCreate(BaseModel):
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class TaskResponse(TaskBase):
    id: int
    date: datetime
    author_id: int
    assigned_users: List[UserResponse]

    class Config:
        orm_mode = True
