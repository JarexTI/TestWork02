from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskStatus, TaskUpdate


async def create_task(
    db: AsyncSession,
    task: TaskCreate,
    current_user: User
) -> Task:
    """
    Создание новой задачи.
    """
    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        owner_id=current_user.id,
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


async def update_task(
    db: AsyncSession,
    task_id: int,
    task_update: TaskUpdate,
    current_user: User
) -> Task:
    """
    Полное обновление существующей задачи.
    """
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.owner_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Задача с id {task_id} не найдена или не принадлежит вам'
        )

    for field, value in task_update.dict().items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


async def get_task_list(
    db: AsyncSession,
    task_status: Optional[TaskStatus] = None,
    priority: Optional[int] = None,
    created_at: Optional[datetime] = None,
) -> list[Task]:
    """
    Получение списка задач с возможной фильтрацией по статусу,
    приоритету и дате создания.
    """
    query = select(Task)

    if task_status:
        query = query.where(Task.status == task_status)
    if priority:
        query = query.where(Task.priority == priority)
    if created_at:
        query = query.where(func.date(Task.created_at) == created_at.date())

    result = await db.execute(query)
    return list(result.scalars().all())


async def search_tasks(
    db: AsyncSession,
    query_str: str
) -> list[Task]:
    """
    Поиск задач по подстроке в названии или описании.
    """
    query = select(Task).where(
        Task.title.ilike(f'%{query_str}%') |
        Task.description.ilike(f'%{query_str}%')
    )
    result = await db.execute(query)
    return list(result.scalars().all())
