from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Rental(Base):
    """대여/반납 정보"""
    __tablename__ = "rental"
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    rental_id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey("reservation.reservation_id"), nullable=True)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("item.item_id"), nullable=False)
    cable = Column(Boolean, default=False)
    rented_on = Column(DateTime, nullable=False)
    due_on = Column(DateTime, nullable=False)
    returned_on = Column(DateTime, nullable=True)

    # relationships
    reservation = relationship("Reservation", backref="rental")
    member = relationship("User", backref="rentals")
    item = relationship("Item", backref="rentals")


