from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.user import User  # Импортируем модель User
from schemas.user_schema import (
    UserCreate,
    UserLogin,
    UserChangePassword,
    UserUpdateToken,
    UserResponse,
    UserChangePasswordResponse 
)
from database.database import SessionLocal, engine  # Импортируем SessionLocal и engine
import secrets

auth_router = APIRouter()

# Создание таблиц в базе данных (если они еще не созданы)
User.metadata.create_all(bind=engine)

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
    
    # Создаем пользователя без токена
    new_user = User(
        username=user.username,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        token=None  # Токен не генерируется при регистрации
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"username": user.username, "message": "User registered successfully"}

@auth_router.post("/login", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username, User.password == user.password).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Если токен отсутствует, генерируем новый
    if not db_user.token:
        db_user.token = secrets.token_hex(16)  # Генерация 32-символьного токена
        db.commit()
        db.refresh(db_user)
    
    # Возвращаем токен в ответе
    return {"username": user.username, "token": db_user.token, "message": "Login successful"}

@auth_router.post("/change-password", response_model=UserChangePasswordResponse)
def change_password(user: UserChangePassword, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем старый пароль
    if db_user.password != user.old_password:
        raise HTTPException(status_code=401, detail="Invalid old password")
    
    # Обновляем пароль
    db_user.password = user.new_password
    db.commit()
    db.refresh(db_user)
    
    return {"username": user.username, "message": "Password changed successfully"}

@auth_router.post("/update-token", response_model=UserResponse)
def update_token(user: UserUpdateToken, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Генерация нового случайного токена
    new_token = secrets.token_hex(16)  # Генерация 32-символьного токена
    
    # Обновляем токен
    db_user.token = new_token
    db.commit()
    db.refresh(db_user)
    
    # Возвращаем новый токен в ответе
    return {"username": user.username, "token": new_token, "message": "Token updated successfully"}