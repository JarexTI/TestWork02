from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.jwt import create_token, verify_token
from app.core.password import get_hash_password, verify_password
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


async def register_user(
    db: AsyncSession,
    name: str,
    email: str,
    password: str
) -> User:
    """
    Регистрация нового пользователя.
    """
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email уже зарегистрирован'
        )

    user = User(
        name=name,
        email=email,
        hashed_password=get_hash_password(password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
) -> User | None:
    """
    Аутентификация пользователя по email и паролю.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        return None

    return user


def update_access_token(user_id: int) -> str:
    """
    Обновление access токена.
    """
    return create_token(
        {'sub': str(user_id)},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def generate_token_pair(user_id: int) -> tuple[str, str]:
    """
    Генерация пары access и refresh токенов.
    """
    access_token = update_access_token(user_id)
    refresh_token = create_token(
        {'sub': str(user_id)},
        timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    return access_token, refresh_token


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Получение текущего авторизованного пользователя по токену.
    """
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    user_id = int(payload.get('sub'))

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    return user
