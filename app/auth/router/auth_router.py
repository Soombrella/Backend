from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.schema.auth import UserCreate, UserLogin, RegisterResponse, LoginResponse
from app.auth.service.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """회원가입"""
    auth_service = AuthService(db)
    return auth_service.register_user(user_data)


@router.post("/login", response_model=LoginResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """로그인"""
    auth_service = AuthService(db)
    return auth_service.authenticate_user(login_data)

