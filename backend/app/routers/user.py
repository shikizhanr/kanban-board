from app.schemas.user import ChangePasswordRequest,  RefreshTokenRequest, Token
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.database import get_db
from app.services.auth import (
    get_current_user,
    refresh_access_token,
)
from app.utils.security import get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


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

@router.post("/refresh-token", response_model=Token)
async def refresh_token_no_auth(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    new_token = await refresh_access_token(request.username, db)
    return {"access_token": new_token, "token_type": "bearer"}