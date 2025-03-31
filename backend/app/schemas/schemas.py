from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    first_name: str
    last_name: str

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: Optional[str] = None
    status: Optional[str] = "Запланировано"

class TaskResponse(TaskBase):
    id: int
    date: datetime
    author_id: int
    assigned_users: List[UserBase]