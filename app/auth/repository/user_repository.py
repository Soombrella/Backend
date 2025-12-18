from sqlalchemy.orm import Session
from typing import Optional

from app.auth.model.user import Member
from app.manage.model.bank_account import BankAccount
from app.auth.schema.auth import UserCreate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_student_no(self, student_no: str) -> Optional[Member]:
        return self.db.query(Member).filter(Member.student_no == student_no).first()

    def get_by_email(self, email: str) -> Optional[Member]:
        return self.db.query(Member).filter(Member.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[Member]:
        return self.db.query(Member).filter(Member.member_id == user_id).first()

    def create(self, user_data: UserCreate, password_hash: str) -> Member:
        """회원 + 계좌 동시 생성"""

        member = Member(
            name=user_data.name,
            department=user_data.department,
            student_no=user_data.student_no,
            phone=user_data.phone,
            email=user_data.email,
            password_hash=password_hash,
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)

        bank_account = BankAccount(
            member_id=member.member_id,
            account_bank=user_data.account_bank,
            account_num=user_data.account_num,
        )
        self.db.add(bank_account)
        self.db.commit()

        return member

    def delete_user(self, user: Member):
        self.db.delete(user)
        self.db.commit()

    def update_password(self, user: Member, password_hash: str) -> Member:
        user.password_hash = password_hash
        self.db.commit()
        self.db.refresh(user)
        return user
