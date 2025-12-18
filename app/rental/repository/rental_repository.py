from sqlalchemy.orm import Session, joinedload

from app.auth.model.user import Member
from app.manage.model.item import Item, ItemCategory
from app.manage.model.rental import Rental
from app.manage.model.reservation import Reservation
from app.manage.model.deposit_txn import DepositTxn


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
    
    def get_rental_detail(self, rental_id: int):
        """
        단일 대여 상세 조회
        """
        return (
            self.db.query(Rental)
            .options(
                joinedload(Rental.item).joinedload(Item.category),
                joinedload(Rental.reservation),
            )
            .filter(Rental.rental_id == rental_id)
            .first()
        )

    def has_deposit(self, member_id: int, item_id: int) -> bool:
        return (
            self.db.query(DepositTxn)
            .filter(
                DepositTxn.member_id == member_id,
                DepositTxn.item_id == item_id,
                DepositTxn.reason == "DEPOSIT",
            )
            .first()
            is not None
        )

    def has_refund(self, member_id: int, item_id: int) -> bool:
        return (
            self.db.query(DepositTxn)
            .filter(
                DepositTxn.member_id == member_id,
                DepositTxn.item_id == item_id,
                DepositTxn.reason == "REFUND",
            )
            .first()
            is not None
        )
