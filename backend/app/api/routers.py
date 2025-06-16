from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File
from datetime import timedelta
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.services import tasks as tasks_service
from app.services import users as users_service
from app.core.security import create_access_token, verify_password, get_current_user
from app.models.user import User
import shutil
import os

# Главный роутер, который будет подключен в main.py
router = APIRouter()

UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)


@router.post("/users/me/avatar", response_model=UserOut)
async def upload_avatar_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Создаем безопасный путь к файлу
    file_path = os.path.join(UPLOADS_DIR, f"{current_user.id}_{file.filename}")
    
    # Сохраняем файл на диск
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Обновляем путь в базе данных
    # В ответе вернется относительный путь, например, 'uploads/1_my_avatar.png'
    # Фронтенд должен будет добавить к нему базовый URL бэкенда.
    return await users_service.update_avatar(db, user=current_user, avatar_path=file_path)

# НОВЫЙ ЭНДПОИНТ, чтобы Nginx мог раздавать статичные файлы
# (это не самый лучший способ, но простой для нашего проекта)
from fastapi.staticfiles import StaticFiles
router.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


# --- Роутер аутентификации ---
@router.post("/auth/token", response_model=Token)
async def login_for_access_token(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_service.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Теперь timedelta будет найдена
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Роутер пользователей ---
@router.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await users_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await users_service.create_user(db=db, user=user)

@router.get("/users/", response_model=List[UserOut])
async def read_users_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Защищаем эндпоинт
):
    """Возвращает список всех пользователей."""
    return await users_service.get_users(db)

# --- Роутер задач (с аутентификацией) ---
@router.post("/tasks/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await tasks_service.create_task(db=db, task=task, creator_id=current_user.id)

@router.get("/tasks/", response_model=List[TaskOut])
async def read_tasks_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await tasks_service.get_tasks(db)

@router.get("/tasks/{task_id}", response_model=TaskOut)
async def read_task_endpoint(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_task = await tasks_service.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task_endpoint(
    task_id: int,
    task: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ВАЖНО: Проверяем, существует ли исполнитель, если его ID передан
    if task.assignee_id is not None:
        assignee = await users_service.get_user(db, user_id=task.assignee_id)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {task.assignee_id} not found to be an assignee."
            )

    # Проверяем, существует ли сама задача
    updated_task = await tasks_service.update_task(db, task_id=task_id, task_data=task)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return updated_task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted_task = await tasks_service.delete_task(db, task_id=task_id)
    if deleted_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
@router.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Возвращает данные о текущем аутентифицированном пользователе.
    """
    return current_user