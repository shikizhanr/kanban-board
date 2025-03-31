from fastapi import APIRouter, HTTPException, Depends, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.user import User
from schemas.user_schema import (
    UserCreate,
    UserLogin,
    UserChangePassword,
    UserUpdateToken,
    UserResponse,
    UserChangePasswordResponse
)
from database.database import SessionLocal, engine
import secrets

auth_router = APIRouter()

# Создание таблиц в базе данных
User.metadata.create_all(bind=engine)

# Класс для проверки JWT токена
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not self.verify_token(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or expired token"
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code"
            )

    def verify_token(self, token: str) -> bool:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.token == token).first()
            return user is not None
        finally:
            db.close()

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@auth_router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(
        username=user.username,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        token=None
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"username": user.username, "message": "User registered successfully"}

@auth_router.post("/login", response_model=UserResponse)
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username, User.password == user.password).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not db_user.token:
        db_user.token = secrets.token_hex(16)
        db.commit()
        db.refresh(db_user)
    
    response.set_cookie(
        key="access_token",
        value=db_user.token,
        httponly=True,
        max_age=900,
        expires=900,
        secure=True,
        samesite="lax"
    )
    
    return {"username": user.username, "token": db_user.token, "message": "Login successful"}

@auth_router.post("/change-password", response_model=UserChangePasswordResponse)
def change_password(user: UserChangePassword, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.password != user.old_password:
        raise HTTPException(status_code=401, detail="Invalid old password")
    
    db_user.password = user.new_password
    db.commit()
    db.refresh(db_user)
    
    return {"username": user.username, "message": "Password changed successfully"}

@auth_router.post("/update-token", response_model=UserResponse)
def update_token(user: UserUpdateToken, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_token = secrets.token_hex(16)
    db_user.token = new_token
    db.commit()
    db.refresh(db_user)
    
    response.set_cookie(
        key="access_token",
        value=new_token,
        httponly=True,
        max_age=900,
        expires=900,
        secure=True,
        samesite="lax"
    )
    
    return {"username": user.username, "token": new_token, "message": "Token updated successfully"}

@auth_router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

@auth_router.get("/protected", dependencies=[Depends(JWTBearer())])
async def protected_route():
    return {"message": "This is a protected route"}

@auth_router.get("/check-auth", dependencies=[Depends(JWTBearer())])
async def check_auth(request: Request):
    token = request.cookies.get("access_token")
    return {"message": "Authenticated", "token": token}