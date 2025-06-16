from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.task import Task, task_user_association # Removed TaskStatus, TaskProfile from models to use Schema versions for query
from ..models.user import User
from ..services.auth import get_current_user
from ..schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskLogTimeRequest,
    TaskStatusUpdateRequest, # Add this
    TaskStatus as SchemaTaskStatus, # Use aliased schema enum for query params
    TaskProfile as SchemaTaskProfile # Use aliased schema enum for query params
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
        task: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Corrected: Initialize db_task_data first
    db_task_data = task.dict(exclude_unset=True, exclude={'assigned_user_ids'})
    # task_profile and status will be taken from task_data if provided, else model defaults
    db_task = Task(**db_task_data, author_id=current_user.id) # author_id is current_user.id

    if task.assigned_user_ids:
        # Filter by User.id for assigned users
        users = db.query(User).filter(User.id.in_(task.assigned_user_ids)).all()
        db_task.assigned_users = users

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdateRequest, # Use the new schema
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    is_author = db_task.author_id == current_user.id
    # Efficient check for assignee
    is_assigned = db.query(task_user_association).filter(
        task_user_association.c.task_id == task_id,
        task_user_association.c.user_id == current_user.id
    ).first() is not None

    if not (is_author or is_assigned):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the task author or an assigned user can update the status"
        )

    db_task.status = status_update.status # status_update.status is already a TaskStatus enum value
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

    # Check access rights: task author or if user is assigned to the task
    is_author = task.author_id == current_user.id
    is_assigned = current_user in task.assigned_users

    if not (is_author or is_assigned):
        # If user is neither the author nor assigned, check if they are an admin/superuser
        # For now, let's assume only author or assigned can view. This can be expanded.
        # if not current_user.is_superuser: # Example if a superuser concept exists
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task"
        )
    return task

@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), # Added current_user dependency
    status: Optional[SchemaTaskStatus] = Query(None), # Use aliased SchemaTaskStatus
    task_profile: Optional[SchemaTaskProfile] = Query(None), # Use aliased SchemaTaskProfile
    author_id: Optional[int] = Query(None),
    assigned_user_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100
):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status) # Model's Task.status will compare correctly with SchemaTaskStatus value
    if task_profile:
        query = query.filter(Task.task_profile == task_profile) # Model's Task.task_profile with SchemaTaskProfile
    if author_id:
        query = query.filter(Task.author_id == author_id)
    if assigned_user_id:
        # Join with task_user_association table and then with User table to filter by assigned user's ID
        query = query.join(task_user_association).join(User).filter(User.id == assigned_user_id)

    tasks = query.offset(skip).limit(limit).all()
    return tasks


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

    # Only the author can update the task
    if db_task.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks"
        )

    update_data = task_update.dict(exclude_unset=True)

    # Handle assigned_user_ids separately if present in the update
    if 'assigned_user_ids' in update_data:
        assigned_user_ids = update_data.pop('assigned_user_ids')
        if assigned_user_ids is not None: # Allow clearing assignments with empty list
            users = db.query(User).filter(User.id.in_(assigned_user_ids)).all()
            db_task.assigned_users = users
        else: # if assigned_user_ids is explicitly None, do not change existing
            pass


    for field, value in update_data.items():
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

    # Only the author can delete the task
    if task.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tasks"
        )

    db.delete(task)
    db.commit()
    # return {"message": "Task deleted successfully"} # This message won't be sent due to 204
                                                  # but good for consistency if status changes.
                                                  # Better to return Response(status_code=204)
    # No return message for 204
    return


@router.post("/{task_id}/assign/{user_id_to_assign}", response_model=TaskResponse)
def assign_user_to_task(
    task_id: int,
    user_id_to_assign: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if db_task.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the task author can assign users")

    user_to_assign = db.query(User).filter(User.id == user_id_to_assign).first()
    if not user_to_assign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to assign not found")

    if user_to_assign not in db_task.assigned_users:
        db_task.assigned_users.append(user_to_assign)
        db.commit()
        db.refresh(db_task)

    return db_task

@router.delete("/{task_id}/unassign/{user_id_to_unassign}", response_model=TaskResponse)
def unassign_user_from_task(
    task_id: int,
    user_id_to_unassign: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if db_task.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the task author can unassign users")

    user_to_unassign = db.query(User).filter(User.id == user_id_to_unassign).first()
    if not user_to_unassign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to unassign not found")

    if user_to_unassign in db_task.assigned_users:
        db_task.assigned_users.remove(user_to_unassign)
        db.commit()
        db.refresh(db_task)
    # else:
        # If user is not assigned, we can either raise an error or return the task as is.
        # For now, if not assigned, it does nothing and returns the task. (Idempotent)
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not assigned to this task")

    return db_task


# Commented out filter functions are removed as requested.
# Old get_tasks_by_type, get_tasks_by_date, etc. are removed.
# Old edit_task_description, etc. are removed.

@router.post("/{task_id}/log_time", response_model=TaskResponse)
def log_time_for_task(
    task_id: int,
    log_time_request: TaskLogTimeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    is_author = db_task.author_id == current_user.id
    # Efficient check for assignee
    is_assigned = db.query(task_user_association).filter(
        task_user_association.c.task_id == task_id,
        task_user_association.c.user_id == current_user.id
    ).first() is not None

    if not (is_author or is_assigned):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the task author or an assigned user can log time"
        )

    db_task.time_spent += log_time_request.time_added
    db.commit()
    db.refresh(db_task)
    return db_task