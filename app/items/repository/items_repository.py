from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime

from app.manage.model.item import Item, ItemCategory
from app.manage.model.reservation import Reservation


class ItemsRepository:
    def __init__(self, db: Session):
        self.db = db

    # ==================== Category 관련 ====================

    def get_category_by_name(self, category_name: str) -> Optional[ItemCategory]:
        """카테고리명으로 카테고리 조회"""
        return self.db.query(ItemCategory).filter(
            ItemCategory.category_name == category_name
        ).first()

    def get_all_categories(self) -> List[ItemCategory]:
        """모든 카테고리 조회"""
        return self.db.query(ItemCategory).all()

    # ==================== Item 관련 ====================

    def get_available_item_by_category(self, category_id: int) -> Optional[Item]:
        """해당 카테고리에서 사용 가능한 물품 1개 조회 (첫 번째 또는 랜덤)"""
        return self.db.query(Item).filter(
            Item.category_id == category_id,
            Item.status == "AVAILABLE"
        ).first()

    def get_available_count_by_category(self, category_id: int) -> int:
        """해당 카테고리의 사용 가능한 물품 수 조회"""
        return self.db.query(Item).filter(
            Item.category_id == category_id,
            Item.status == "AVAILABLE"
        ).count()

    def get_all_available_counts(self) -> List[dict]:
        """모든 카테고리별 사용 가능한 물품 수 조회"""
        result = self.db.query(
            ItemCategory.category_name,
            func.count(Item.item_id).label("available_count")
        ).outerjoin(
            Item, 
            (ItemCategory.category_id == Item.category_id) & (Item.status == "AVAILABLE")
        ).group_by(
            ItemCategory.category_id,
            ItemCategory.category_name
        ).all()
        
        return [
            {"category_name": row.category_name, "available_count": row.available_count}
            for row in result
        ]

    def update_item_status(self, item: Item, status: str) -> Item:
        """물품 상태 업데이트"""
        item.status = status
        self.db.commit()
        self.db.refresh(item)
        return item

    # ==================== Reservation 관련 ====================

    def create_reservation(
        self,
        member_id: int,
        item_id: int,
        cable: bool,
        pickup_on: datetime,
        proxy_return: bool = False,
    ) -> Reservation:
        """예약 생성"""
        reservation = Reservation(
            member_id=member_id,
            item_id=item_id,
            cable=cable,
            pickup_on=pickup_on,
            status="PENDING",
        )
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

