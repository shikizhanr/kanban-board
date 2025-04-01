from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..services.auth import get_current_user, get_db
from ..schemas.user import User
from ..models.user import User as UserModel

router = APIRouter()


@router.get("/me", response_model=User)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user
