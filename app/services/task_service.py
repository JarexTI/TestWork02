from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy import select
from datetime import datetime

from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatus


async def create_task(
    db: AsyncSession,
    task: TaskCreate,
    current_user: User
) -> Task:
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
    task_up: TaskUpdate,
    current_user: User,
) -> Task:
    query = select(Task).where(
        Task.id == task_id,
        Task.owner_id == current_user.id
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Задача с id {task_id} не найдена или не принадлежит Вам'
        )

    for field, value in task_up.dict().items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


async def get_task_list(
    db: AsyncSession,
    status: TaskStatus | None = None,
    priority: int | None = None,
    created_at: datetime | None = None,
) -> list[Task]:
    query = select(Task)

    if status:
        query = query.where(Task.status == status)
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
    query = select(Task).where(
        Task.title.ilike(f'%{query_str}%') |
        Task.description.ilike(f'%{query_str}%')
    )
    result = await db.execute(query)
    return list(result.scalars().all())
