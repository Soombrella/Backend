from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.schema.auth import (
    UserCreate,
    UserLogin,
    RegisterResponse,
    LoginResponse,
    WithdrawRequest,
    WithdrawResponse,
)
from app.auth.service.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

# 🔐 Swagger / Front / curl 전부 호환되는 Bearer 인증
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> str:
    """
    Authorization: Bearer <JWT>
    """
    token = credentials.credentials

    student_no = AuthService.verify_token(token)
    if not student_no:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return student_no


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return auth_service.register_user(user_data)


@router.post("/login", response_model=LoginResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return auth_service.authenticate_user(login_data)


@router.post("/withdraw", response_model=WithdrawResponse)
def withdraw(
    withdraw_data: WithdrawRequest,
    student_no: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    return auth_service.withdraw_user(student_no, withdraw_data)
