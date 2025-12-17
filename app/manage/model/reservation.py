from sqlalchemy import Column, Integer, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Reservation(Base):
    """예약 정보"""
    __tablename__ = "reservation"
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    reservation_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("item.item_id"), nullable=False)
    cable = Column(Boolean, default=False)
    pickup_on = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    # status: PENDING, CONFIRMED, CANCELLED 등

    # relationships
    member = relationship("User", backref="reservations")
    item = relationship("Item", backref="reservations")

