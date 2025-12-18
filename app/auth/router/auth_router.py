from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_obj
from app.db.database import get_db
from app.auth.service.auth_service import AuthService
from app.auth.schema.auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    UserCreate,
    UserLogin,
    RegisterResponse,
    LoginResponse,
    WithdrawRequest,
    WithdrawResponse,
    FindPwResponse,
    AuthCodeRequest,
    AuthCodeVerify,
)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    student_no = AuthService.verify_token(credentials.credentials)
    if not student_no:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return student_no


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return AuthService(db).register_user(user_data)


@router.post("/login", response_model=LoginResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    return AuthService(db).authenticate_user(login_data)


@router.delete("/withdraw", response_model=WithdrawResponse)
def withdraw(
    withdraw_data: WithdrawRequest,
    student_no: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AuthService(db).withdraw_user(student_no, withdraw_data)


@router.post("/find-pw/request", response_model=FindPwResponse)
def request_auth_code(request_data: AuthCodeRequest, db: Session = Depends(get_db)):
    return AuthService(db).request_auth_code(request_data.email)


@router.post("/find-pw/verify", response_model=FindPwResponse)
def verify_auth_code(verify_data: AuthCodeVerify, db: Session = Depends(get_db)):
    return AuthService(db).verify_auth_code(
        verify_data.email,
        verify_data.code
    )

@router.patch(
    "/password",
    response_model=ChangePasswordResponse,
    summary="비밀번호 변경",
)
def change_password(
    data: ChangePasswordRequest,
    current_user = Depends(get_current_user_obj),
    db: Session = Depends(get_db),
):
    return AuthService(db).change_password(current_user, data)