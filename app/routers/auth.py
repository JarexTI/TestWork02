from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.jwt import verify_token
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, TokenPair, TokenRefresh
from app.services.auth_service import (register_user,
                                       authenticate_user,
                                       update_access_token,
                                       generate_token_pair)

router = APIRouter()


@router.post('/register', response_model=TokenPair)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = register_user(db, user.name, user.email, user.password)
    access_token, refresh_token = generate_token_pair(db_user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post('/login', response_model=TokenPair)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token, refresh_token = generate_token_pair(db_user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh", response_model=TokenPair)
def refresh(refresh_data: TokenRefresh):
    payload = verify_token(refresh_data.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = int(payload.get("sub"))
    access_token = update_access_token(user_id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_data.refresh_token
    }
