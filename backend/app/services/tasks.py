from fastapi import HTTPException
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


from sqlalchemy import case # Import case

async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Получает список всех задач с пагинацией, отсортированных по приоритету и дате создания."""
    
    priority_order = case(
        (Task.priority == 'high', 0),
        (Task.priority == 'medium', 1),
        (Task.priority == 'low', 2),
        else_=3 
    )

    result = await db.execute(
        select(Task)
        .options(selectinload(Task.creator), selectinload(Task.assignees))
        .order_by(priority_order, Task.created_at.desc()) # Sort by priority, then by creation date
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_tasks_by_assignee(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    """
    Получает список задач, созданных пользователем или назначенных ему,
    отсортированных по приоритету и дате создания.
    """
    priority_order = case(
        (Task.priority == 'high', 0),
        (Task.priority == 'medium', 1),
        (Task.priority == 'low', 2),
        else_=3 
    )

    result = await db.execute(
        select(Task)
        .options(selectinload(Task.creator), selectinload(Task.assignees))
        .filter(
            (Task.creator_id == user_id) | (Task.assignees.any(User.id == user_id))
        )
        .order_by(priority_order, Task.created_at.desc())
        .offset(skip)
        .limit(limit)
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

async def update_task(db: AsyncSession, task_id: int, task_data: TaskUpdate, current_user: User):
    db_task = await get_task(db, task_id)
    if not db_task:
        return None

    update_data = task_data.model_dump(exclude_unset=True)

    if "status" in update_data and current_user.id not in [assignee.id for assignee in db_task.assignees]:
        raise HTTPException(status_code=403, detail="Вы не назначены на выполнение этой задачи")

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