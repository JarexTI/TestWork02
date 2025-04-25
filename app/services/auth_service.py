from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.password import get_hash_password, verify_password
from app.core.jwt import create_token, verify_token
from app.core.config import settings
from app.db.session import get_db
from datetime import timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


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
    if not user or not verify_password(password, user_hash_pass):
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


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
