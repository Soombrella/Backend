from datetime import datetime, timedelta, timezone
from typing import Optional
import random
import string
import os

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.auth.repository.user_repository import UserRepository
from app.auth.repository.auth_code_repository import AuthCodeRepository
from app.auth.schema.auth import UserCreate, UserLogin, WithdrawRequest

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.auth_code_repo = AuthCodeRepository(db)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def register_user(self, user_data: UserCreate) -> dict:
        if self.user_repo.get_by_student_no(user_data.student_no):
            raise HTTPException(400, "Student number already registered")

        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(400, "Email already registered")

        hashed_password = self.get_password_hash(user_data.password)
        user = self.user_repo.create(user_data, hashed_password)

        return {
            "success": True,
            "message": "회원가입 성공",
            "data": {
                "member_id": user.member_id,
                "student_no": user.student_no,
            },
        }

    def authenticate_user(self, login_data: UserLogin) -> dict:
        user = self.user_repo.get_by_student_no(login_data.student_no)
        if not user or not self.verify_password(login_data.password, user.password_hash):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

        token = self.create_access_token({"sub": user.student_no})

        return {
            "success": True,
            "message": "로그인 성공",
            "data": {
                "member_id": user.member_id,
                "student_no": user.student_no,
                "name": user.name,
                "department": user.department,
                "email": user.email,
                "is_admin": user.is_admin,
                "token": token,
            },
        }

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("sub")
        except JWTError:
            return None

    def withdraw_user(self, student_no: str, withdraw_data: WithdrawRequest) -> dict:
        user = self.user_repo.get_by_student_no(student_no)
        if not user:
            raise HTTPException(404, "User not found")

        if not self.verify_password(withdraw_data.current_password, user.password_hash):
            raise HTTPException(401, "Incorrect password")

        self.user_repo.delete_user(user)
        return {"success": True, "message": "회원 탈퇴 완료"}

    def request_auth_code(self, email: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(404, "User not found")

        code = ''.join(str(random.randint(0, 9)) for _ in range(6))
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        self.auth_code_repo.create(email=email, code=code, expires_at=expires_at)

        print(f"[DEBUG] auth code: {email} -> {code}")
        return {"success": True, "message": "인증번호가 이메일로 전송되었습니다."}

    def verify_auth_code(self, email: str, code: str) -> dict:
        if not self.auth_code_repo.verify_code(email, code):
            raise HTTPException(400, "Invalid or expired code")

        user = self.user_repo.get_by_email(email)
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.user_repo.update_password(user, self.get_password_hash(temp_password))
        self.auth_code_repo.delete_by_email(email)

        print(f"[DEBUG] temp password: {email} -> {temp_password}")
        return {"success": True, "message": "임시 비밀번호를 이메일로 발송했습니다."}
