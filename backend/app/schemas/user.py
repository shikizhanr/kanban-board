from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserOut(UserBase):
    id: int
    avatar_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)