from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

async def get_task(db: AsyncSession, task_id: int):
    """
    Получает одну задачу по ID. Эта функция уже умеет правильно подгружать
    связи creator и assignee.
    """
    result = await db.execute(
        select(Task).options(selectinload(Task.creator), selectinload(Task.assignee)).filter(Task.id == task_id)
    )
    return result.scalars().first()

async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Получает список всех задач с пагинацией."""
    result = await db.execute(
        select(Task).options(selectinload(Task.creator), selectinload(Task.assignee)).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create_task(db: AsyncSession, task: TaskCreate, creator_id: int):
    """
    Создает новую задачу и возвращает ее с полной информацией,
    включая создателя и исполнителя.
    """
    db_task = Task(**task.model_dump(), creator_id=creator_id)
    
    db.add(db_task)
    await db.commit()
    # ИСПРАВЛЕНО: Явно обновляем объект из БД, чтобы получить его ID и другие поля.
    await db.refresh(db_task)

    # Теперь, когда у db_task есть ID, мы можем безопасно его использовать.
    # Вызов get_task по-прежнему полезен, т.к. он гарантирует загрузку связей.
    return await get_task(db, db_task.id)

async def update_task(db: AsyncSession, task_id: int, task_data: TaskUpdate):
    """Обновляет данные задачи."""
    db_task = await get_task(db, task_id)
    if not db_task:
        return None

    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    await db.commit()
    await db.refresh(db_task)
    
    return await get_task(db, db_task.id)

async def delete_task(db: AsyncSession, task_id: int):
    db_task = await get_task(db, task_id)
    if not db_task:
        return None
    await db.delete(db_task)
    await db.commit()
    return db_task

async def assign_task_to_user(db: AsyncSession, task_id: int, user_id: int):
    db_task = await get_task(db, task_id)
    if not db_task:
        return None
    db_task.assignee_id = user_id
    await db.commit()
    await db.refresh(db_task)
    return await get_task(db, db_task.id)

async def log_time_for_task(db: AsyncSession, task_id: int, time_to_add: float):
    db_task = await get_task(db, task_id)
    if not db_task:
        return None
    db_task.time_spent += time_to_add
    await db.commit()
    await db.refresh(db_task)
    return await get_task(db, db_task.id)