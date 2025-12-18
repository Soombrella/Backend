from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.auth.model.user import Member
from app.auth.service.auth_service import AuthService
from app.auth.repository.user_repository import UserRepository

security = HTTPBearer()


def get_current_user_obj(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Member:
    """
    JWT 토큰에서 사용자 정보를 추출하고 User 객체 반환
    """
    token = credentials.credentials
    
    student_no = AuthService.verify_token(token)
    if not student_no:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_student_no(student_no)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


def get_current_admin_user(
    current_user: Member = Depends(get_current_user_obj),
) -> Member:
    """
    관리자 권한 체크 - is_admin이 True인 사용자만 통과
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return current_user

