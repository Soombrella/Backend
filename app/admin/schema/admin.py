from pydantic import BaseModel
from typing import Optional, List


# ==================== 공통 응답 ====================

class AdminResponse(BaseModel):
    """공통 응답"""
    success: bool
    message: str


# ==================== Category 관련 ====================

class CategoryCreate(BaseModel):
    """카테고리 생성 요청"""
    category_name: str
    deposit_required: int = 0


class CategoryUpdate(BaseModel):
    """카테고리 수정 요청"""
    category_name: Optional[str] = None
    deposit_required: Optional[int] = None


class CategoryResponse(BaseModel):
    """카테고리 정보 응답"""
    category_id: int
    category_name: str
    deposit_required: int

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """카테고리 목록 응답"""
    success: bool
    message: str
    data: List[CategoryResponse]


class CategoryDetailResponse(BaseModel):
    """카테고리 단일 조회 응답"""
    success: bool
    message: str
    data: CategoryResponse


# ==================== Item 관련 ====================

class ItemCreate(BaseModel):
    """
    물품 생성 요청
    
    - category_name: "umbrella" (우산) 또는 "powerbank" (보조배터리)
    """
    category_name: str
    serial_no: Optional[str] = None
    status: str = "AVAILABLE"


class ItemFullUpdate(BaseModel):
    """
    물품 전체 수정 요청
    
    - category_name: "umbrella" (우산) 또는 "powerbank" (보조배터리)
    """
    category_name: Optional[str] = None
    serial_no: Optional[str] = None
    status: Optional[str] = None


class ItemResponse(BaseModel):
    """물품 정보 응답"""
    item_id: int
    category_id: int
    category_name: str
    serial_no: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    """물품 목록 응답"""
    success: bool
    message: str
    data: List[ItemResponse]


class ItemDetailResponse(BaseModel):
    """물품 단일 조회 응답"""
    success: bool
    message: str
    data: ItemResponse

