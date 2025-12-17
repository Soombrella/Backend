from pydantic import BaseModel
from typing import List, Optional


# ==================== 1. 물품 대여 예약 (POST /items/rent) ====================

class RentRequest(BaseModel):
    """
    물품 대여 예약 요청
    
    - category_name: 물품 종류 (우산, 보조배터리)
    - pickup_on: 방문 예정일 (YYYY-MM-DD)
    - cable: 보조배터리 케이블 여부 (케이블 대여X or 우산 → false)
    - proxy_return: 대리 반납 여부
    """
    category_name: str
    pickup_on: str  # "2025-11-01" 형식
    cable: bool = False
    proxy_return: bool = False


class RentResponse(BaseModel):
    """물품 대여 예약 응답"""
    success: bool
    message: str


# ==================== 2. 물품 재고 수 조회 (GET /items/available/count) ====================

class AvailableCountItem(BaseModel):
    """카테고리별 재고 수"""
    category_name: str
    available_count: int


class AvailableCountResponse(BaseModel):
    """
    물품 재고 수 조회 응답
    
    카테고리 구분 필요 시 QueryString으로 확장 가능
    예: /items/available/count?category_id=2
    """
    success: bool
    message: str
    data: List[AvailableCountItem]

