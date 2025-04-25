from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Схема для регистрации пользователя"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description='Имя пользователя'
    )
    email: EmailStr = Field(
        ...,
        description='Электронная почта'
    )
    password: str = Field(
        ...,
        min_length=6,
        description='Пароль (не менее 6 символов)'
    )


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr = Field(
        ...,
        description='Электронная почта'
    )
    password: str = Field(
        ...,
        description='Пароль'
    )


class UserResponse(BaseModel):
    """Схема пользователя, возвращаемая в ответе"""
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class TokenPair(BaseModel):
    """Схема с парой токенов (access + refresh)"""
    access_token: str = Field(
        ...,
        description='JWT access токен'
    )
    refresh_token: str = Field(
        ...,
        description='JWT refresh токен'
    )


class TokenRefresh(BaseModel):
    """Схема для запроса обновления access-токена"""
    refresh_token: str = Field(
        ...,
        description='Refresh токен'
    )
