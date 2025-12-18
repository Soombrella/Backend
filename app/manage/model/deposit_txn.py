from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class DepositTxn(Base):
    """보증금 입출금 내역"""
    __tablename__ = "deposit_txn"
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    deposit_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("member.member_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("item.item_id"), nullable=False)
    amount = Column(Integer, nullable=False)
    reason = Column(String(20), nullable=False)  # DEPOSIT, REFUND 등
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    member = relationship("Member", backref="deposit_txns")
    item = relationship("Item", backref="deposit_txns")

