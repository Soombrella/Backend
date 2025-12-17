from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.auth.model.user import User
from app.auth.dependencies import get_current_admin_user
from app.manage.service.manage_service import ManageService
from app.manage.schema.manage import (
    UserRentalListResponse,
    UserRentalStatusUpdate,
    UserRentalUpdateResponse,
    ItemListResponse,
    ItemUpdate,
    ItemUpdateResponse,
    ManageResponse,
)

router = APIRouter(prefix="/manage", tags=["manage (관리자)"])


# ==================== 공통 응답 정의 ====================

# 조회 API 응답
GET_RESPONSES = {
    200: {"description": "정상 처리"},
    401: {"description": "인증 필요 (토큰 없음/만료)"},
    403: {"description": "권한 부족"},
    500: {"description": "Internal Server Error"},
}

# 수정 API 응답
PATCH_RESPONSES = {
    200: {"description": "정상 처리"},
    400: {"description": "잘못된 요청"},
    401: {"description": "인증 필요 (토큰 없음/만료)"},
    403: {"description": "권한 부족"},
    404: {"description": "대상이 존재하지 않음"},
    500: {"description": "Internal Server Error"},
}

# 삭제 API 응답
DELETE_RESPONSES = {
    200: {"description": "정상 처리"},
    400: {"description": "잘못된 요청"},
    401: {"description": "인증 필요 (토큰 없음/만료)"},
    403: {"description": "권한 부족"},
    404: {"description": "대상이 존재하지 않음"},
    500: {"description": "Internal Server Error"},
}


# ==================== User 관련 ====================

@router.get(
    "/users",
    response_model=UserRentalListResponse,
    responses=GET_RESPONSES,
    summary="학생 대여 목록 조회",
    description="모든 학생의 대여 정보를 조회합니다. (관리자 전용)",
)
def get_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    service = ManageService(db)
    return service.get_all_user_rentals()


@router.patch(
    "/users/{user_id}",
    response_model=UserRentalUpdateResponse,
    responses=PATCH_RESPONSES,
    summary="학생 대여 목록 수정",
    description="""
학생의 대여 상태를 수정합니다. (관리자 전용)

**status 값:**
- `대여중`: 예약 → 대여 시작
- `반납완료`: 반납 처리
- `환급완료`: 환급 처리
- `예약취소`: 예약 취소
    """,
)
def update_user(
    user_id: int,
    update_data: UserRentalStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    service = ManageService(db)
    return service.update_user_rental_status(user_id, update_data)


@router.delete(
    "/users/{user_id}",
    response_model=UserRentalUpdateResponse,
    responses=DELETE_RESPONSES,
    summary="학생 대여 목록 삭제",
    description="학생의 예약/대여 정보를 삭제합니다. (관리자 전용)",
)
def delete_user_rentals(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    service = ManageService(db)
    return service.delete_user_rentals(user_id)


# ==================== Item 관련 ====================

@router.get(
    "/items",
    response_model=ItemListResponse,
    responses=GET_RESPONSES,
    summary="재고 목록 조회",
    description="모든 재고를 조회합니다. (관리자 전용)",
)
def get_items(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    service = ManageService(db)
    return service.get_all_items()


@router.patch(
    "/items/{item_id}",
    response_model=ItemUpdateResponse,
    responses=PATCH_RESPONSES,
    summary="재고 목록 수정",
    description="""
재고 상태를 수정합니다. (관리자 전용)

**status 값:**
- `사용가능`
- `대여중`
- `반납완료`
- `분실 및 고장`
- `예약중`
    """,
)
def update_item(
    item_id: int,
    update_data: ItemUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    service = ManageService(db)
    return service.update_item(item_id, update_data)


@router.delete(
    "/items/{item_id}",
    response_model=ItemUpdateResponse,
    responses=DELETE_RESPONSES,
    summary="재고 목록 삭제",
    description="재고를 삭제합니다. (관리자 전용)",
)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    service = ManageService(db)
    return service.delete_item(item_id)
