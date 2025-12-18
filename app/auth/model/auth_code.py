from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.database import Base

class AuthCode(Base):
    __tablename__ = "auth_code"
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    member_id = Column(
        Integer,
        ForeignKey("member.member_id", ondelete="CASCADE"),
        primary_key=True
    )

    email = Column(String(255), index=True, nullable=False)
    code_hash = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
