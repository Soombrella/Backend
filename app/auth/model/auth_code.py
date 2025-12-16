from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.database import Base

class AuthCode(Base):
    __tablename__ = "auth_codes"
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    email = Column(String(255), index=True, nullable=False)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
