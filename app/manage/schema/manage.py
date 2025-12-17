from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ==================== 1. 학생 대여 목록 조회 (GET /manage/users) ====================

class MemberInfo(BaseModel):
    """회원 정보 (중첩)"""
    member_id: int
    name: str
    student_no: str


class ItemInfo(BaseModel):
    """물품 정보 (중첩)"""
    item_id: int
    category_name: str
    cable: bool


class TimelineInfo(BaseModel):
    """타임라인 정보 (중첩)"""
    pickup_on: Optional[datetime] = None      # 대여예정일 (예약된 픽업 시간)
    rented_on: Optional[datetime] = None      # 실제 대여일
    due_on: Optional[datetime] = None         # 반납예정일
    returned_on: Optional[datetime] = None    # 실제 반납일


class RefundAccountInfo(BaseModel):
    """환불 계좌 정보 (중첩)"""
    account_bank: str
    account_num: str


class UserRentalItem(BaseModel):
    """학생 대여 목록 개별 항목"""
    reservation_id: int
    rental_id: Optional[int] = None
    member: MemberInfo
    item: ItemInfo
    timeline: TimelineInfo
    status: str                               # 예약중, 대여중, 환급전 등
    refund_account: RefundAccountInfo

    class Config:
        from_attributes = True


class UserRentalListResponse(BaseModel):
    """학생 대여 목록 응답 (GET /manage/users)"""
    success: bool
    message: str
    data: List[UserRentalItem]


# ==================== 2. 학생 대여 목록 수정 (PATCH /manage/users/{user_id}) ====================

class UserRentalStatusUpdate(BaseModel):
    """
    학생 대여 상태 수정 요청
    
    status 값:
    - "대여중": 예약 → 대여 시작 (rental 생성)
    - "반납완료": 반납 처리 (returned_on 설정)
    - "환급완료": 환급 처리 (deposit_txn에 환급 기록)
    - "예약취소": 예약 취소
    """
    status: str
    reservation_id: Optional[int] = None  # 특정 예약 건 지정 (선택) - 특정 대여 건 수정을 위해 필요할 것 같음


class UserRentalUpdateResponse(BaseModel):
    """학생 대여 상태 수정 응답"""
    success: bool
    message: str


# ==================== 4. 재고 목록 조회 (GET /manage/items) ====================

class ItemResponse(BaseModel):
    """재고 정보 응답"""
    item_id: int
    category_name: str
    serial_no: Optional[str] = None
    status: str  # 사용가능, 대여중, 반납완료, 분실 및 고장

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    """재고 목록 응답"""
    success: bool
    message: str
    data: List[ItemResponse]


# ==================== 5. 재고 수정 (PATCH /manage/items/{item_id}) ====================

class ItemUpdate(BaseModel):
    """
    재고 정보 수정 요청
    
    status 값 (한글):
    - "사용가능"
    - "대여중"
    - "반납완료"
    - "분실 및 고장"
    - "예약중"
    """
    status: str


class ItemUpdateResponse(BaseModel):
    """재고 수정 응답"""
    success: bool
    message: str


# ==================== 공통 응답 ====================

class ManageResponse(BaseModel):
    """공통 응답"""
    success: bool
    message: str
    data: Optional[dict] = None
