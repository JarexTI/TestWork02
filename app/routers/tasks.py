from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskStatus, TaskUpdate
from app.services.auth_service import get_current_user
from app.services.task_service import (create_task, get_task_list,
                                       search_tasks, update_task)

router = APIRouter()


@router.post('/', response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task_view(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_task(db, task, current_user)


@router.put('/{task_id}', response_model=TaskRead)
async def update_task_view(
    task_id: int,
    task: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await update_task(db, task_id, task, current_user)


@router.get('/', response_model=list[TaskRead])
async def list_tasks_view(
    task_status: TaskStatus | None = Query(None, alias='status'),
    priority: int | None = Query(None, ge=1, le=10),
    created_at: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    if not any([task_status, priority, created_at]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Хотя бы один параметр фильтрации должен быть задан'
        )
    return await get_task_list(db, task_status, priority, created_at)


@router.get('/search', response_model=list[TaskRead])
async def search_tasks_view(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    return await search_tasks(db, q)
