from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Member(Base):
    __tablename__ = "member"
    __table_args__ = {"mysql_charset": "utf8mb4"}

    member_id = Column(Integer, primary_key=True, index=True)
    student_no = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 계좌 관계
    bank_account = relationship(
        "BankAccount",
        back_populates="member",
        uselist=False,
        cascade="all, delete"
    )
