from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.database import get_db
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.task import (
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse
)


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
def create_task(
        task: TaskCreate,
        db: Session = Depends(get_db),
        author_id: int = 1  # Временная заглушка
):
    try:
        db_task = Task(
            title=task.title,
            description=task.description,
            task_type=task.task_type,
            status=task.status,
            ##status=TaskStatus(task.status),
            author_id=author_id
        )

        if task.assigned_user_ids:
            users = db.query(User).filter(User.id.in_(task.assigned_user_ids)).all()
            db_task.assigned_users = users

        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
        task_id: int,
        task_update: TaskUpdate,
        db: Session = Depends(get_db)
):
    try:
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")

        for field, value in task_update.dict(exclude_unset=True).items():
            if field == "assigned_user_ids":
                users = db.query(User).filter(User.id.in_(value)).all()
                db_task.assigned_users = users
            else:
                setattr(db_task, field, value)

        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        db.delete(task)
        db.commit()
        return {"message": "Task deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


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