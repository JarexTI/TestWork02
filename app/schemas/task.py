from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    pending = 'pending'
    done = 'done'


class TaskBase(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=40,
        description='Название задачи'
    )
    description: Optional[str] = Field(
        None,
        description='Описание задачи'
    )
    status: TaskStatus = Field(
        default=TaskStatus.pending,
        description='pending или done'
    )
    priority: int = Field(
        ge=1,
        le=10,
        description='1 — самый высокий, 10 — самый низкий'
    )


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True
