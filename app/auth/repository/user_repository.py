from sqlalchemy.orm import Session
from app.auth.model.user import User
from app.auth.schema.auth import UserCreate
from typing import Optional


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_student_no(self, student_no: str) -> Optional[User]:
        """학번으로 사용자 조회"""
        return self.db.query(User).filter(User.student_no == student_no).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user_data: UserCreate, hashed_password: str) -> User:
        """새 사용자 생성"""
        db_user = User(
            name=user_data.name,
            department=user_data.department,
            student_no=user_data.student_no,
            phone=user_data.phone,
            email=user_data.email,
            account_bank=user_data.account_bank,
            account_num=user_data.account_num,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user: User):
        self.db.delete(user)
        self.db.commit()
    
    def update_password(self, user: User, hashed_password: str) -> User:
        """비밀번호 업데이트"""
        user.hashed_password = hashed_password
        self.db.commit()
        self.db.refresh(user)
        return user

