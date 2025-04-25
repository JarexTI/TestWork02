from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.base import Base


class TaskStatus(PyEnum):
    pending = 'pending'
    done = 'done'


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    title = Column(
        String,
        nullable=False
    )
    description = Column(
        String,
        nullable=True
    )
    status = Column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.pending
    )
    priority = Column(
        Integer,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    owner_id = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=False
    )
