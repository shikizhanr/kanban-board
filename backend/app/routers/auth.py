from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.schemas.user import UserCreate, UserLogin, Token, UserResponse, RefreshTokenRequest, ChangePasswordRequest
from app.models.user import User
from app.services.auth import (
    create_access_token,
    get_current_user,
    refresh_access_token,
    verify_user_active
)
from app.database import get_db
from app.utils.security import get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}
    
@router.post("/refresh-token", response_model=Token)
async def refresh_token_no_auth(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    new_token = await refresh_access_token(request.username, db)
    return {"access_token": new_token, "token_type": "bearer"}

@router.put("/change-password", status_code=200)
async def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(request.current_password, user.password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    user.password = get_password_hash(request.new_password)
    db.commit()
    return {"message": "Password updated successfully"}