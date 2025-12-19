from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.auth.model.user import Member
from app.auth.dependencies import get_current_admin_user
from app.admin.service.admin_service import AdminService
from app.admin.schema.admin import (
    CategoryCreate,
    CategoryUpdate,
    CategoryListResponse,
    CategoryDetailResponse,
    AdminResponse,
    ItemCreate,
    ItemFullUpdate,
    ItemListResponse,
    ItemDetailResponse,
)

router = APIRouter(prefix="/admin", tags=["admin (관리자 - 카테고리/물품 관리)"])


# ==================== 공통 응답 정의 ====================

GET_RESPONSES = {
    200: {"description": "정상 처리"},
    401: {"description": "인증 필요 (토큰 없음/만료)"},
    403: {"description": "권한 부족 (관리자만 접근 가능)"},
    500: {"description": "서버 오류"},
}

POST_RESPONSES = {
    201: {"description": "생성 성공"},
    400: {"description": "잘못된 요청 (중복, 유효성 검사 실패 등)"},
    401: {"description": "인증 필요"},
    403: {"description": "권한 부족"},
    500: {"description": "서버 오류"},
}

PATCH_RESPONSES = {
    200: {"description": "수정 성공"},
    400: {"description": "잘못된 요청"},
    401: {"description": "인증 필요"},
    403: {"description": "권한 부족"},
    404: {"description": "대상을 찾을 수 없음"},
    500: {"description": "서버 오류"},
}

DELETE_RESPONSES = {
    200: {"description": "삭제 성공"},
    400: {"description": "삭제 불가 (연관 데이터 존재 등)"},
    401: {"description": "인증 필요"},
    403: {"description": "권한 부족"},
    404: {"description": "대상을 찾을 수 없음"},
    500: {"description": "서버 오류"},
}


# ==================== Category API ====================

@router.get(
    "/categories",
    response_model=CategoryListResponse,
    responses=GET_RESPONSES,
    summary="카테고리 목록 조회",
    description="모든 카테고리를 조회합니다. (관리자 전용)",
)
def get_categories(
    db: Session = Depends(get_db),
    admin: Member = Depends(get_current_admin_user),
):
    service = AdminService(db)
    return service.get_all_categories()


@router.get(
    "/categories/{category_id}",
    response_model=CategoryDetailResponse,
    responses={**GET_RESPONSES, 404: {"description": "카테고리를 찾을 수 없음"}},
    summary="카테고리 단일 조회",
    description="특정 카테고리를 조회합니다. (관리자 전용)",
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: Member = Depends(get_current_admin_user),
):
    service = AdminService(db)
    return service.get_category_by_id(category_id)


@router.post(
    "/categories",
    response_model=CategoryDetailResponse,
    responses=POST_RESPONSES,
    status_code=201,
    summary="카테고리 생성",
    description="""
새로운 카테고리를 생성합니다. (관리자 전용)

**요청 예시:**
```json
{
  "category_name": "노트북",
  "deposit_required": 50000
}
```
    """,
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    admin: Member = Depends(get_current_admin_user),
):
    service = AdminService(db)
    return service.create_category(data)


@router.patch(
    "/categories/{category_id}",
    response_model=AdminResponse,
    responses=PATCH_RESPONSES,
    summary="카테고리 수정",
    description="""
카테고리 정보를 수정합니다. (관리자 전용)

**요청 예시:**
```json
{
  "category_name": "우산",
  "deposit_required": 10000
}
```
    """,
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    admin: Member = Depends(get_current_admin_user),
):
    service = AdminService(db)
    return service.update_category(category_id, data)


@router.delete(
    "/categories/{category_id}",
    response_model=AdminResponse,
    responses=DELETE_RESPONSES,
    summary="카테고리 삭제",
    description="카테고리를 삭제합니다. 해당 카테고리에 물품이 있으면 삭제할 수 없습니다. (관리자 전용)",
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: Member = Depends(get_current_admin_user),
):
    service = AdminService(db)
    return service.delete_category(category_id)


# ==================== Item API ====================

@router.get(
    "/items",
    response_model=ItemListResponse,
    responses=GET_RESPONSES,
    summary="물품 목록 조회",
    description="모든 물품을 조회합니다. (관리자 전용)",
)
def get_items(
    db: Session = Depends(get_db),
    admin: Member = Depends(get_current_admin_user),
):
    service = AdminService(db)
    return service.get_all_items()


@router.get(
    "/items/{item_id}",
    response_model=ItemDetailResponse,
    responses={**GET_RESPONSES, 404: {"description": "물품을 찾을 수 없음"}},
    summary="물품 단일 조회",
    description="특정 물품을 조회합니다. (관리자 전용)",
)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin: Member = Depends(get_current_admin_user),
):
    service = AdminService(db)
    return service.get_item_by_id(item_id)


@router.post(
    "/items",
    response_model=ItemDetailResponse,
    responses=POST_RESPONSES,
    status_code=201,
    summary="물품 생성",
    description="""
새로운 물품을 등록합니다. (관리자 전용)

**요청 예시:**
```json
{
  "category_id": 1,
  "serial_no": "UMB-001",
  "status": "AVAILABLE"
}
```

**status 값:**
- `AVAILABLE`: 사용 가능
- `RENTED`: 대여중
- `RESERVED`: 예약중
- `BROKEN`: 분실 및 고장
    """,
)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    admin: Member = Depends(get_current_admin_user),
):
    service = AdminService(db)
    return service.create_item(data)


@router.patch(
    "/items/{item_id}",
    response_model=AdminResponse,
    responses=PATCH_RESPONSES,
    summary="물품 수정",
    description="""
물품 정보를 수정합니다. (관리자 전용)

**요청 예시:**
```json
{
  "category_id": 2,
  "serial_no": "PB-001",
  "status": "AVAILABLE"
}
```
    """,
)
def update_item(
    item_id: int,
    data: ItemFullUpdate,
    db: Session = Depends(get_db),
    admin: Member = Depends(get_current_admin_user),
):
    service = AdminService(db)
    return service.update_item(item_id, data)


@router.delete(
    "/items/{item_id}",
    response_model=AdminResponse,
    responses=DELETE_RESPONSES,
    summary="물품 삭제",
    description="물품을 삭제합니다. 연관된 예약/대여/보증금 내역도 함께 삭제됩니다. (관리자 전용)",
)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin: Member = Depends(get_current_admin_user),
):
    service = AdminService(db)
    return service.delete_item(item_id)
