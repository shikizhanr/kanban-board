from ..database import SessionLocal
from ..models.task import Task, TaskStatus
from ..schemas.task import TaskBase
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date


def create_task(session: Session, task_info: TaskBase, author_id):
    try:
        task = Task(
            title=task_info.title,
            description=task_info.description,
            task_type=task_info.task_type,
            status=task_info.status,
            author_id=author_id
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        return True

    except Exception as error:
        return False


def delete_task(session: Session, task_id: int):
    try:
        task = session.get(Task, task_id)
        if task:
            session.delete(task)
            session.commit()
            return True
        return False

    except Exception as error:
        return False


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


def get_tasks_by_type(session: Session, task_type: str, offset: int, limit: int):
    return session.scalars(select(Task).where(Task.task_type == task_type).offset(offset).limit(limit)).all()


def get_tasks_by_date(session: Session, task_date: date, offset: int, limit: int):
    return session.scalars(select(Task).where(Task.date == task_date).offset(offset).limit(limit)).all()


def get_tasks_by_author(session: Session, author_id: int, offset: int, limit: int):
    return session.scalars(select(Task).where(Task.author_id == author_id).offset(offset).limit(limit)).all()


def get_tasks_by_status(session: Session, status: TaskStatus, offset: int, limit: int):
    return session.scalars(select(Task).where(Task.status == status).offset(offset).limit(limit)).all()
