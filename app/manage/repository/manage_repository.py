from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta

from app.auth.model.user import Member
from app.manage.model.item import Item, ItemCategory
from app.manage.model.rental import Rental
from app.manage.model.reservation import Reservation
from app.manage.model.bank_account import BankAccount
from app.manage.model.deposit_txn import DepositTxn


class ManageRepository:
    def __init__(self, db: Session):
        self.db = db

    # ==================== Reservation 관련 (학생 대여 목록) ====================

    def get_all_reservations_with_details(self) -> List[Reservation]:
        """모든 예약 정보 조회 (회원, 물품, 대여 정보 포함)"""
        return self.db.query(Reservation).options(
            joinedload(Reservation.member),
            joinedload(Reservation.item).joinedload(Item.category),
            joinedload(Reservation.rental),
        ).all()

    def get_reservation_by_id(self, reservation_id: int) -> Optional[Reservation]:
        """ID로 예약 정보 조회"""
        return self.db.query(Reservation).options(
            joinedload(Reservation.member),
            joinedload(Reservation.item).joinedload(Item.category),
            joinedload(Reservation.rental),
        ).filter(Reservation.reservation_id == reservation_id).first()

    def get_reservations_by_member_id(self, member_id: int) -> List[Reservation]:
        """회원 ID로 예약 목록 조회"""
        return self.db.query(Reservation).options(
            joinedload(Reservation.member),
            joinedload(Reservation.item).joinedload(Item.category),
            joinedload(Reservation.rental),
        ).filter(Reservation.member_id == member_id).all()

    def update_reservation_status(self, reservation: Reservation, status: str) -> Reservation:
        """예약 상태 업데이트"""
        reservation.status = status
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def delete_user_reservations_and_rentals(self, member_id: int) -> None:
        """사용자의 모든 예약/대여 정보 삭제"""
        # 대여 정보 삭제
        self.db.query(Rental).filter(Rental.member_id == member_id).delete()
        
        # 예약 정보 삭제
        self.db.query(Reservation).filter(Reservation.member_id == member_id).delete()
        
        # 보증금 거래 내역 삭제
        self.db.query(DepositTxn).filter(DepositTxn.member_id == member_id).delete()
        
        self.db.commit()

    # ==================== User 관련 ====================

    def get_all_users(self) -> List[Member]:
        """모든 사용자 조회"""
        return self.db.query(Member).all()

    def get_user_by_id(self, user_id: int) -> Optional[Member]:
        """ID로 사용자 조회"""
        return self.db.query(Member).filter(Member.member_id == user_id).first()

    def delete_user(self, user: Member) -> None:
        """사용자 삭제"""
        self.db.delete(user)
        self.db.commit()

    # ==================== BankAccount 관련 ====================

    def get_bank_account_by_member_id(self, member_id: int) -> Optional[BankAccount]:
        """회원 ID로 계좌 정보 조회"""
        return self.db.query(BankAccount).filter(
            BankAccount.member_id == member_id
        ).first()

    # ==================== Item 관련 ====================

    def get_all_items(self) -> List[Item]:
        """모든 재고 조회"""
        return self.db.query(Item).options(
            joinedload(Item.category)
        ).all()

    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """ID로 재고 조회"""
        return self.db.query(Item).options(
            joinedload(Item.category)
        ).filter(Item.item_id == item_id).first()

    def update_item(self, item: Item, update_data: dict) -> Item:
        """재고 정보 수정"""
        for key, value in update_data.items():
            if value is not None:
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item: Item) -> None:
        """재고 삭제"""
        self.db.delete(item)
        self.db.commit()

    # ==================== Rental 관련 ====================

    def get_rental_by_id(self, rental_id: int) -> Optional[Rental]:
        """ID로 대여 정보 조회"""
        return self.db.query(Rental).filter(Rental.rental_id == rental_id).first()

    def get_rental_by_reservation_id(self, reservation_id: int) -> Optional[Rental]:
        """예약 ID로 대여 정보 조회"""
        return self.db.query(Rental).filter(
            Rental.reservation_id == reservation_id
        ).first()

    def create_rental(self, reservation: Reservation, due_days: int = 1) -> Rental:
        """대여 생성 (예약 → 대여)"""
        now = datetime.now()
        rental = Rental(
            reservation_id=reservation.reservation_id,
            member_id=reservation.member_id,
            item_id=reservation.item_id,
            cable=reservation.cable,
            rented_on=now,
            due_on=now + timedelta(days=due_days),
        )
        self.db.add(rental)
        
        # 예약 상태 업데이트
        reservation.status = "CONFIRMED"
        
        # 물품 상태 업데이트
        item = self.db.query(Item).filter(Item.item_id == reservation.item_id).first()
        if item:
            item.status = "RENTED"
        
        self.db.commit()
        self.db.refresh(rental)
        return rental

    def set_returned_on(self, rental: Rental) -> Rental:
        """반납 처리"""
        rental.returned_on = datetime.now()
        
        # 물품 상태 업데이트
        item = self.db.query(Item).filter(Item.item_id == rental.item_id).first()
        if item:
            item.status = "AVAILABLE"
        
        self.db.commit()
        self.db.refresh(rental)
        return rental

    def update_rental(self, rental: Rental, update_data: dict) -> Rental:
        """대여 정보 수정"""
        for key, value in update_data.items():
            if value is not None:
                setattr(rental, key, value)
        self.db.commit()
        self.db.refresh(rental)
        return rental

    # ==================== DepositTxn 관련 ====================

    def create_deposit_refund(self, member_id: int, item_id: int, amount: int) -> DepositTxn:
        """보증금 환급 기록 생성"""
        txn = DepositTxn(
            member_id=member_id,
            item_id=item_id,
            amount=amount,
            reason="REFUND",
        )
        self.db.add(txn)
        self.db.commit()
        self.db.refresh(txn)
        return txn

    def get_deposit_by_reservation(self, member_id: int, item_id: int) -> Optional[DepositTxn]:
        """예약에 대한 보증금 조회"""
        return self.db.query(DepositTxn).filter(
            DepositTxn.member_id == member_id,
            DepositTxn.item_id == item_id,
            DepositTxn.reason == "DEPOSIT",
        ).first()

    # ==================== Category 관련 ====================

    def get_category_by_id(self, category_id: int) -> Optional[ItemCategory]:
        """ID로 카테고리 조회"""
        return self.db.query(ItemCategory).filter(
            ItemCategory.category_id == category_id
        ).first()
