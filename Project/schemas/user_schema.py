from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserChangePassword(BaseModel):
    username: str 
    old_password: str
    new_password: str

class UserUpdateToken(BaseModel):
    username: str

class UserResponse(BaseModel):
    username: str
    token: str
    message: str

class UserChangePasswordResponse(BaseModel):
    username: str
    message: str