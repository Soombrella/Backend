from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from app.auth.repository.user_repository import UserRepository
from app.auth.schema.auth import UserCreate, UserLogin

load_dotenv()

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """비밀번호 해싱"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """JWT 액세스 토큰 생성"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def register_user(self, user_data: UserCreate) -> dict:
        # 🔒 bcrypt 72 byte 제한 체크 (필수)
        password_bytes = user_data.password.encode("utf-8")
        print("",password_bytes)
        if len(password_bytes) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password too long (max 72 bytes for bcrypt)"
            )

        # 학번 중복 확인
        if self.user_repo.get_by_student_no(user_data.student_no):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student number already registered"
            )

        # 이메일 중복 확인
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # 비밀번호 해싱 (딱 1번)
        hashed_password = self.get_password_hash(user_data.password)

        # 사용자 생성
        user = self.user_repo.create(user_data, hashed_password)

        return {
            "success": True,
            "message": "회원가입 성공",
            "data": {
                "member_id": user.id,
                "student_no": user.student_no,
                "name": user.name
            }
        }


    def authenticate_user(self, login_data: UserLogin) -> dict:
        """로그인"""
        # 사용자 조회 (학번으로)
        user = self.user_repo.get_by_student_no(login_data.student_no)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect student number or password"
            )
        
        # 비밀번호 검증
        if not self.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect student number or password"
            )
        
        # 활성화 상태 확인
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        # JWT 토큰 생성 (학번을 sub에 저장)
        access_token = self.create_access_token(data={"sub": user.student_no})
        
        return {
            "success": True,
            "message": "로그인 성공",
            "data": {
                "member_id": user.id,
                "student_no": user.student_no,
                "name": user.name,
                "department": user.department,
                "email": user.email,
                "is_admin": user.is_admin,
                "token": access_token
            }
        }

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """JWT 토큰 검증 및 학번 추출"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            student_no: str = payload.get("sub")
            if student_no is None:
                return None
            return student_no
        except JWTError:
            return None

