from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import verify_token
from app.db.session import get_db
from app.schemas.user import (TokenPair, TokenRefresh, UserCreate, UserLogin,
                              UserResponse)
from app.services.auth_service import (authenticate_user, generate_token_pair,
                                       register_user, update_access_token)

router = APIRouter()


@router.post(
    '/register',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    db_user = await register_user(db, user.name, user.email, user.password)
    return db_user


@router.post('/login', response_model=TokenPair)
async def login(
    user: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    db_user = await authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=400,
            detail='Неверные учетные данные'
        )

    access_token, refresh_token = generate_token_pair(db_user.id)
    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.post('/refresh', response_model=TokenPair)
async def refresh(refresh_data: TokenRefresh):
    payload = verify_token(refresh_data.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Недопустимый токен обновления'
        )

    user_id = int(payload.get('sub'))
    access_token = update_access_token(user_id)

    return {
        'access_token': access_token,
        'refresh_token': refresh_data.refresh_token
    }
