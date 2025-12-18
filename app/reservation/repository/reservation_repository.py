from sqlalchemy.orm import Session

from app.auth.model.user import Member
from app.manage.model.reservation import Reservation
from app.manage.model.item import Item, ItemCategory
from app.manage.model.deposit_txn import DepositTxn


class ReservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_reservation_detail(self, reservation_id: int, student_no: str):
        return (
            self.db.query(Reservation, Item, ItemCategory)
            .join(Member, Reservation.member_id == Member.member_id)
            .join(Item, Reservation.item_id == Item.item_id)
            .join(ItemCategory, Item.category_id == ItemCategory.category_id)
            .filter(
                Reservation.reservation_id == reservation_id,
                Member.student_no == student_no,
            )
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
