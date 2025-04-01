from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from ..database import get_db
from ..models.task import Task, TaskStatus
from ..models.user import User
from ..services.auth import get_current_user
from ..schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


# Все эндпоинты требуют аутентификации
@router.post("/", response_model=TaskResponse)
def create_task(
        task: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_task = Task(
        **task.dict(exclude={'assigned_user_ids'}),
        author_id=current_user.user_id  # Используем ID текущего пользователя
    )

    if task.assigned_user_ids:
        users = db.query(User).filter(User.user_id.in_(task.assigned_user_ids)).all()
        db_task.assigned_users = users

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверка прав доступа
    if task.author_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task"
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
        task_id: int,
        task_update: TaskUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверка прав на изменение
    if db_task.author_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks"
        )

    # Обновление полей
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/{task_id}")
def delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверка прав на удаление
    if task.author_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tasks"
        )

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


"""
def edit_task_description(session: Session, task_description: str, task_id: int):
    try:
        task = session.get(Task, task_id)
        if task:
            task.description = task_description
            session.commit()
            session.refresh(task)

            return True
        return False

    except Exception as error:
        return False


def edit_task_title(session: Session, task_title: str, task_id: int):
    try:
        task = session.get(Task, task_id)
        if task:
            task.title = task_title
            session.commit()
            session.refresh(task)

            return True
        return False

    except Exception as error:
        return False


def edit_task_type(session: Session, task_type: str, task_id: int):
    try:
        task = session.get(Task, task_id)
        if task:
            task.task_type = task_type
            session.commit()
            session.refresh(task)

            return True
        return False

    except Exception as error:
        return False


def edit_task_status(session: Session, task_status: TaskStatus, task_id: int):
    try:
        task = session.get(Task, task_id)
        if task:
            task.status = task_status
            session.commit()
            session.refresh(task)

            return True
        return False

    except Exception as error:
        return False

# Методы фильтрации
@router.get("/by_type/", response_model=List[TaskResponse])
def get_tasks_by_type(
        task_type: str,
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    return db.query(Task).filter(Task.task_type == task_type) \
        .offset(offset).limit(limit).all()


@router.get("/by_date/", response_model=List[TaskResponse])
def get_tasks_by_date(
        task_date: date,
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    return db.query(Task).filter(Task.date == task_date) \
        .offset(offset).limit(limit).all()


@router.get("/by_author/", response_model=List[TaskResponse])
def get_tasks_by_author(
        author_id: int,
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    return db.query(Task).filter(Task.author_id == author_id) \
        .offset(offset).limit(limit).all()


@router.get("/by_status/", response_model=List[TaskResponse])
def get_tasks_by_status(
        status: TaskStatus,
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    return db.query(Task).filter(Task.status == status) \
        .offset(offset).limit(limit).all()
"""