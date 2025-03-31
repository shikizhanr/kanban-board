from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..routers.tasks import (
    create_task, delete_task, edit_task_description, edit_task_title,
    edit_task_type, edit_task_status, get_tasks_by_author, get_tasks_by_status
)
from ..models.task import Task, TaskStatus
from ..schemas.task import TaskBase, TaskUpdate


def create_task_service(session: Session, task_data: TaskBase, user_id: int):
    # Создаёт задачу, если у пользователя есть права.
    if not create_task(session, task_data, user_id):
        raise HTTPException(status_code=400, detail="Ошибка создания задачи")
    return {"detail": "Задача успешно создана"}


def delete_task_service(session: Session, task_id: int, user_id: int):
    # Удаляет задачу, если пользователь — автор
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.author_id != user_id:
        raise HTTPException(status_code=403, detail="Вы не можете удалить эту задачу")

    if not delete_task(session, task_id):
        raise HTTPException(status_code=500, detail="Ошибка удаления задачи")
    return {"detail": "Задача успешно удалена"}


def update_task_service(session: Session, task_id: int, user_id: int, task_update: TaskUpdate):
    # Обновляет задачу с проверкой прав и бизнес-логики.
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.author_id != user_id:
        raise HTTPException(status_code=403, detail="Вы не можете редактировать эту задачу")

    # Если задача завершена, нельзя изменить её статус
    if task_update.status and task.status == TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Нельзя изменять выполненную задачу")

    # Обновляем только те поля, которые пришли в запросе
    if task_update.title is not None:
        edit_task_title(session, task_update.title, task_id)
    if task_update.description is not None:
        edit_task_description(session, task_update.description, task_id)
    if task_update.task_type is not None:
        edit_task_type(session, task_update.task_type, task_id)
    if task_update.status is not None:
        edit_task_status(session, task_update.status, task_id)

    return {"detail": "Задача успешно обновлена"}


def get_filtered_tasks(session: Session, author_id: int = None, status: TaskStatus = None, offset: int = 0, limit: int = 10):
    # Фильтрует задачи по автору и статусу.
    if author_id:
        return get_tasks_by_author(session, author_id, offset, limit)
    if status:
        return get_tasks_by_status(session, status, offset, limit)
    raise HTTPException(status_code=400, detail="Не указан фильтр")