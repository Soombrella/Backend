from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.manage.model.item import Item, ItemCategory
from app.manage.model.reservation import Reservation
from app.manage.model.rental import Rental
from app.manage.model.deposit_txn import DepositTxn


class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    # ==================== Category 관련 ====================

    def get_all_categories(self) -> List[ItemCategory]:
        """모든 카테고리 조회"""
        return self.db.query(ItemCategory).all()

    def get_category_by_id(self, category_id: int) -> Optional[ItemCategory]:
        """ID로 카테고리 조회"""
        return self.db.query(ItemCategory).filter(
            ItemCategory.category_id == category_id
        ).first()

    def get_category_by_name(self, category_name: str) -> Optional[ItemCategory]:
        """이름으로 카테고리 조회"""
        return self.db.query(ItemCategory).filter(
            ItemCategory.category_name == category_name
        ).first()

    def create_category(self, category_name: str, deposit_required: int = 0) -> ItemCategory:
        """카테고리 생성"""
        category = ItemCategory(
            category_name=category_name,
            deposit_required=deposit_required,
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update_category(self, category: ItemCategory, update_data: dict) -> ItemCategory:
        """카테고리 수정"""
        for key, value in update_data.items():
            if value is not None:
                setattr(category, key, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category: ItemCategory) -> None:
        """카테고리 삭제"""
        self.db.delete(category)
        self.db.commit()

    def get_items_by_category(self, category_id: int) -> List[Item]:
        """카테고리에 속한 물품 조회"""
        return self.db.query(Item).filter(
            Item.category_id == category_id
        ).all()

    # ==================== Item 관련 ====================

    def get_all_items(self) -> List[Item]:
        """모든 물품 조회"""
        return self.db.query(Item).options(
            joinedload(Item.category)
        ).all()

    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """ID로 물품 조회"""
        return self.db.query(Item).options(
            joinedload(Item.category)
        ).filter(Item.item_id == item_id).first()

    def get_item_by_serial_no(self, serial_no: str) -> Optional[Item]:
        """시리얼 번호로 물품 조회"""
        return self.db.query(Item).filter(
            Item.serial_no == serial_no
        ).first()

    def create_item(self, category_id: int, serial_no: Optional[str], status: str = "AVAILABLE") -> Item:
        """물품 생성"""
        item = Item(
            category_id=category_id,
            serial_no=serial_no,
            status=status,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, item: Item, update_data: dict) -> Item:
        """물품 수정"""
        for key, value in update_data.items():
            if value is not None:
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item: Item) -> None:
        """물품 삭제 (연관 데이터 포함)"""
        # 보증금 내역 삭제
        self.db.query(DepositTxn).filter(
            DepositTxn.item_id == item.item_id
        ).delete()

        # 대여 삭제
        self.db.query(Rental).filter(
            Rental.item_id == item.item_id
        ).delete()

        # 예약 삭제
        self.db.query(Reservation).filter(
            Reservation.item_id == item.item_id
        ).delete()

        # 물품 삭제
        self.db.delete(item)
        self.db.commit()

