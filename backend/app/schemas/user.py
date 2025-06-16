from pydantic import BaseModel, Field


class UserBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50) # Updated
    last_name: str = Field(..., min_length=2, max_length=50) # Updated
    username: str = Field(..., max_length=50, pattern="^[a-zA-Z0-9_]+$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    token: str | None = None

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    username: str


class ChangePasswordRequest(BaseModel):
    username: str
    current_password: str
    new_password: str
