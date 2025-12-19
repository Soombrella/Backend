from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.items.repository.items_repository import ItemsRepository
from app.items.schema.items import RentRequest, AvailableCountItem

# 유효한 카테고리명
VALID_CATEGORY_NAMES = ["umbrella", "powerbank"]


class ItemsService:
    def __init__(self, db: Session):
        self.repo = ItemsRepository(db)

    # ==================== 1. 물품 대여 예약 ====================

    def rent_item(self, member_id: int, rent_data: RentRequest) -> dict:
        """
        물품 대여 예약
        
        백엔드 동작 흐름:
        1. category 문자열 → category_id 변환
        2. 해당 category_id의 item 중 status='AVAILABLE'인 item 한 개 선택
        3. 해당 item_id로 reservation insert
        4. 케이블 여부(cable) 저장
        5. pickup_on 저장
        6. proxy_return 저장
        7. item status를 RESERVED로 변경
        """
        # 1. category 문자열 → category_id 변환
        category_name = rent_data.category_name.lower()
        if category_name not in VALID_CATEGORY_NAMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"카테고리 '{rent_data.category_name}'을(를) 찾을 수 없습니다. (umbrella 또는 powerbank 사용)",
            )
        
        category = self.repo.get_category_by_name(category_name)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"카테고리 '{category_name}'을(를) 찾을 수 없습니다.",
            )
        
        # 2. 해당 category_id의 item 중 status='AVAILABLE'인 item 한 개 선택
        available_item = self.repo.get_available_item_by_category(category.category_id)
        if not available_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{category_name}' 카테고리에 대여 가능한 물품이 없습니다.",
            )
        
        # pickup_on 파싱
        try:
            pickup_datetime = datetime.strptime(rent_data.pickup_on, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="pickup_on 형식이 잘못되었습니다. (예: 2025-11-01)",
            )
        
        # 3~6. 예약 생성 (item_id, cable, pickup_on, proxy_return 저장)
        self.repo.create_reservation(
            member_id=member_id,
            item_id=available_item.item_id,
            cable=rent_data.cable,
            pickup_on=pickup_datetime,
            proxy_return=rent_data.proxy_return,
        )
        
        # 7. item status를 RESERVED로 변경
        self.repo.update_item_status(available_item, "RESERVED")
        
        return {
            "success": True,
            "message": "대여 예약 성공",
        }

    # ==================== 2. 물품 재고 수 조회 ====================

    def get_available_count(self, category_id: int = None) -> dict:
        """
        물품 재고 수 조회
        
        - category_id가 없으면 전체 카테고리별 재고 수 반환
        - category_id가 있으면 해당 카테고리만 반환
        """
        if category_id:
            # 특정 카테고리만 조회
            categories = self.repo.get_all_categories()
            target_category = None
            for cat in categories:
                if cat.category_id == category_id:
                    target_category = cat
                    break
            
            if not target_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"카테고리 ID {category_id}를 찾을 수 없습니다.",
                )
            
            count = self.repo.get_available_count_by_category(category_id)
            data = [
                AvailableCountItem(
                    category_name=target_category.category_name,
                    available_count=count,
                )
            ]
        else:
            # 전체 카테고리 조회
            counts = self.repo.get_all_available_counts()
            data = [
                AvailableCountItem(
                    category_name=item["category_name"],
                    available_count=item["available_count"],
                )
                for item in counts
            ]
        
        return {
            "success": True,
            "message": "물품 재고 수 조회 성공",
            "data": data,
        }

