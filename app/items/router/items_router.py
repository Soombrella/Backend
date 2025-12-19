from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.auth.model.user import Member
from app.auth.dependencies import get_current_user_obj
from app.items.service.items_service import ItemsService
from app.items.schema.items import (
    RentRequest,
    RentResponse,
    AvailableCountResponse,
)

router = APIRouter(prefix="/items", tags=["items (비품 대여)"])


# ==================== 공통 응답 정의 ====================

# 대여 예약 API 응답
RENT_RESPONSES = {
    200: {"description": "대여 성공"},
    400: {"description": "카테고리 잘못됨 / 대여 가능한 물품 없음"},
    401: {"description": "로그인 필요"},
    500: {"description": "서버 오류"},
}

# 재고 조회 API 응답
COUNT_RESPONSES = {
    200: {"description": "조회 성공"},
    401: {"description": "로그인 필요"},
    500: {"description": "서버 오류"},
}


# ==================== API 엔드포인트 ====================

@router.post(
    "/rent",
    response_model=RentResponse,
    responses=RENT_RESPONSES,
    summary="물품 대여 예약",
    description="""
물품 대여를 예약합니다. (로그인 필요)

우산 & 보조배터리 모두 이 URL로 신청 정보 보내기

**요청 예시:**
```json
{
  "category_name": "umbrella",
  "pickup_on": "2025-11-01",
  "cable": false,
  "proxy_return": true
}
```

- category_name: "umbrella" (우산) 또는 "powerbank" (보조배터리)
    """,
)
def rent_item(
    rent_data: RentRequest,
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user_obj),
):
    service = ItemsService(db)
    return service.rent_item(current_user.member_id, rent_data)


@router.get(
    "/available/count",
    response_model=AvailableCountResponse,
    responses=COUNT_RESPONSES,
    summary="물품 재고 수 조회",
    description="""
물품 재고 수를 조회합니다. (로그인 필요)

카테고리 구분 필요 시 QueryString으로 확장 가능
예: `/items/available/count?category_id=2`
    """,
)
def get_available_count(
    category_id: Optional[int] = Query(None, description="카테고리 ID (없으면 전체 조회)"),
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user_obj),
):
    service = ItemsService(db)
    return service.get_available_count(category_id)

