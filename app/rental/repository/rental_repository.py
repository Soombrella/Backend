from sqlalchemy.orm import Session

from app.auth.model.user import Member
from app.manage.model.item import Item, ItemCategory
from app.manage.model.rental import Rental
from app.manage.model.reservation import Reservation


class RentalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_student_no(self, student_no: str):
        return (
            self.db.query(Reservation, Rental, Item, ItemCategory)
            .join(Member, Reservation.member_id == Member.member_id)
            .join(Item, Reservation.item_id == Item.item_id)
            .join(ItemCategory, Item.category_id == ItemCategory.category_id)
            .outerjoin(Rental, Reservation.reservation_id == Rental.reservation_id)
            .filter(Member.student_no == student_no)
            .order_by(Reservation.reservation_id.desc())
            .all()
        )
