from pydantic import BaseModel, Field # Added Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

class TaskStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskProfile(str, Enum): # Added
    DEVELOPMENT = "development"
    ANALYTICS = "analytics"
    DOCUMENTATION = "documentation"
    GENERAL = "general"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100) # Updated
    description: Optional[str] = None
    task_profile: Optional[TaskProfile] = TaskProfile.GENERAL # Updated from task_type
    status: Optional[TaskStatus] = TaskStatus.PLANNED
    assigned_user_ids: Optional[List[int]] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    # For updates, most fields should be optional
    title: Optional[str] = Field(None, min_length=3, max_length=100) # Allow title to be None or have value
    description: Optional[str] = None
    task_profile: Optional[TaskProfile] = None # Allow None
    status: Optional[TaskStatus] = None # Allow None
    assigned_user_ids: Optional[List[int]] = None


class TaskResponse(TaskBase):
    id: int
    # date: datetime # Removed
    author_id: int
    assigned_users: List[dict]

    # Added fields
    created_at: datetime
    updated_at: datetime
    time_spent: int
    # task_profile will be inherited from TaskBase and should be present
    # status will be inherited from TaskBase and should be present
    # title will be inherited from TaskBase and should be present

    class Config:
        from_attributes = True

class TaskLogTimeRequest(BaseModel):
    time_added: int = Field(..., gt=0, description="Time added in minutes (must be positive)")

class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatus # Using the existing TaskStatus enum
