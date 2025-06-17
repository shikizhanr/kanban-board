from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from typing import List


async def get_task(db: AsyncSession, task_id: int):
    result = await db.execute(select(Task).options(selectinload(Task.creator), selectinload(Task.assignees)).filter(Task.id == task_id))
    return result.scalars().first()


async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Получает список всех задач с пагинацией."""
    result = await db.execute(
        select(Task).options(selectinload(Task.creator), selectinload(Task.assignees)).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_task(db: AsyncSession, task: TaskCreate, creator_id: int):
    assignee_ids = task.assignee_ids
    task_data = task.model_dump(exclude={"assignee_ids"})
    
    db_task = Task(**task_data, creator_id=creator_id)
    
    if assignee_ids:
        result = await db.execute(select(User).where(User.id.in_(assignee_ids)))
        assignees = result.scalars().all()
        db_task.assignees = assignees

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return await get_task(db, db_task.id)

async def update_task(db: AsyncSession, task_id: int, task_data: TaskUpdate):
    db_task = await get_task(db, task_id)
    if not db_task:
        return None
        
    update_data = task_data.model_dump(exclude_unset=True)

    if "assignee_ids" in update_data:
        assignee_ids = update_data.pop("assignee_ids")
        if assignee_ids is not None:
            result = await db.execute(select(User).where(User.id.in_(assignee_ids)))
            assignees = result.scalars().all()
            db_task.assignees = assignees
        
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