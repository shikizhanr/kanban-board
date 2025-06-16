from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from .user import UserOut
from app.models.task import TaskStatus, TaskType

class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    type: TaskType

class TaskCreate(TaskBase):
    # Исполнителя можно указать при создании
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = None
    type: Optional[TaskType] = None
    status: Optional[TaskStatus] = None
    # Исполнителя можно изменить при обновлении
    assignee_id: Optional[int] = None

class TaskOut(TaskBase):
    id: int
    status: TaskStatus
    time_spent: float
    # ИЗМЕНЕНО: Возвращаем полные объекты создателя и исполнителя
    creator: UserOut
    assignee: Optional[UserOut] = None

    model_config = ConfigDict(from_attributes=True)