from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class BankAccount(Base):
    """은행 계좌 정보"""
    __tablename__ = "bank_account"
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("member.member_id"), nullable=False)
    account_bank = Column(String(20), nullable=False)
    account_num = Column(String(50), nullable=False)

    # relationship
    member = relationship("Member", back_populates="bank_account")

