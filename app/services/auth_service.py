from sqlalchemy.orm import Session
from app.models.user import User
from app.core.password import get_hash_password, verify_password
from app.core.jwt import create_token
from app.core.config import settings
from datetime import timedelta


def register_user(db: Session, name: str, email: str, password: str):
    user = User(
        name=name,
        email=email,
        hashed_password=get_hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def update_access_token(user_id: int) -> str:
    access_token = create_token(
        {"sub": str(user_id)},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return access_token


def generate_token_pair(user_id: int) -> tuple[str, str]:
    access_token = update_access_token(user_id)
    refresh_token = create_token(
        {"sub": str(user_id)},
        timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    return access_token, refresh_token
