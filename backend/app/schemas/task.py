from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime # Added datetime import
from .user import UserOut
from app.models.task import TaskStatus, TaskType

class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    type: TaskType
    priority: str = Field("medium", description="Task priority (e.g., low, medium, high)")

class TaskCreate(TaskBase):
    assignee_ids: Optional[List[int]] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = None
    type: Optional[TaskType] = None
    status: Optional[TaskStatus] = None
    priority: Optional[str] = Field(None, description="Task priority (e.g., low, medium, high)")
    assignee_ids: Optional[List[int]] = None

class TaskOut(TaskBase):
    id: int
    status: TaskStatus
    # priority is inherited from TaskBase and will be included here
    time_spent: float
    created_at: datetime # Added created_at field
    creator: UserOut
    assignees: List[UserOut] = []

    model_config = ConfigDict(from_attributes=True)