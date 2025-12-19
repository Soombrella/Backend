from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.admin.repository.admin_repository import AdminRepository
from app.admin.schema.admin import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    ItemCreate,
    ItemFullUpdate,
    ItemResponse,
)

# 유효한 카테고리명
VALID_CATEGORY_NAMES = ["umbrella", "powerbank"]


class AdminService:
    def __init__(self, db: Session):
        self.repo = AdminRepository(db)

    # ==================== Category 관련 ====================

    def get_all_categories(self) -> dict:
        """모든 카테고리 조회"""
        categories = self.repo.get_all_categories()
        
        result = [
            CategoryResponse(
                category_id=cat.category_id,
                category_name=cat.category_name,
                deposit_required=cat.deposit_required,
            )
            for cat in categories
        ]
        
        return {
            "success": True,
            "message": "카테고리 목록 조회 성공",
            "data": result,
        }

    def get_category_by_id(self, category_id: int) -> dict:
        """카테고리 단일 조회"""
        category = self.repo.get_category_by_id(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다.",
            )
        
        return {
            "success": True,
            "message": "카테고리 조회 성공",
            "data": CategoryResponse(
                category_id=category.category_id,
                category_name=category.category_name,
                deposit_required=category.deposit_required,
            ),
        }

    def create_category(self, data: CategoryCreate) -> dict:
        """카테고리 생성"""
        # 중복 체크
        existing = self.repo.get_category_by_name(data.category_name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{data.category_name}' 카테고리가 이미 존재합니다.",
            )
        
        category = self.repo.create_category(
            category_name=data.category_name,
            deposit_required=data.deposit_required,
        )
        
        return {
            "success": True,
            "message": "카테고리가 생성되었습니다.",
            "data": CategoryResponse(
                category_id=category.category_id,
                category_name=category.category_name,
                deposit_required=category.deposit_required,
            ),
        }

    def update_category(self, category_id: int, data: CategoryUpdate) -> dict:
        """카테고리 수정"""
        category = self.repo.get_category_by_id(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다.",
            )
        
        # 이름 중복 체크 (다른 카테고리와)
        if data.category_name:
            existing = self.repo.get_category_by_name(data.category_name)
            if existing and existing.category_id != category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{data.category_name}' 카테고리가 이미 존재합니다.",
                )
        
        update_dict = {}
        if data.category_name is not None:
            update_dict["category_name"] = data.category_name
        if data.deposit_required is not None:
            update_dict["deposit_required"] = data.deposit_required
        
        updated = self.repo.update_category(category, update_dict)
        
        return {
            "success": True,
            "message": "카테고리가 수정되었습니다.",
        }

    def delete_category(self, category_id: int) -> dict:
        """카테고리 삭제"""
        category = self.repo.get_category_by_id(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다.",
            )
        
        # 해당 카테고리에 물품이 있는지 확인
        items = self.repo.get_items_by_category(category_id)
        if items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"해당 카테고리에 {len(items)}개의 물품이 있어 삭제할 수 없습니다. 물품을 먼저 삭제해주세요.",
            )
        
        self.repo.delete_category(category)
        
        return {
            "success": True,
            "message": "카테고리가 삭제되었습니다.",
        }

    # ==================== Item 관련 ====================

    def get_all_items(self) -> dict:
        """모든 물품 조회"""
        items = self.repo.get_all_items()
        
        result = [
            ItemResponse(
                item_id=item.item_id,
                category_id=item.category_id,
                category_name=item.category.category_name if item.category else "Unknown",
                serial_no=item.serial_no,
                status=item.status,
            )
            for item in items
        ]
        
        return {
            "success": True,
            "message": "물품 목록 조회 성공",
            "data": result,
        }

    def get_item_by_id(self, item_id: int) -> dict:
        """물품 단일 조회"""
        item = self.repo.get_item_by_id(item_id)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="물품을 찾을 수 없습니다.",
            )
        
        return {
            "success": True,
            "message": "물품 조회 성공",
            "data": ItemResponse(
                item_id=item.item_id,
                category_id=item.category_id,
                category_name=item.category.category_name if item.category else "Unknown",
                serial_no=item.serial_no,
                status=item.status,
            ),
        }

    def create_item(self, data: ItemCreate) -> dict:
        """물품 생성"""
        # 카테고리명 검증
        category_name = data.category_name.lower()
        if category_name not in VALID_CATEGORY_NAMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"카테고리 '{data.category_name}'을(를) 찾을 수 없습니다. (umbrella 또는 powerbank 사용)",
            )
        
        # 카테고리 존재 확인
        category = self.repo.get_category_by_name(category_name)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"카테고리 '{category_name}'이(가) DB에 존재하지 않습니다.",
            )
        
        # 시리얼 번호 중복 체크
        if data.serial_no:
            existing = self.repo.get_item_by_serial_no(data.serial_no)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"시리얼 번호 '{data.serial_no}'가 이미 존재합니다.",
                )
        
        # status 유효성 검사
        valid_statuses = ["AVAILABLE", "RENTED", "RESERVED", "BROKEN"]
        if data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 status입니다. 가능한 값: {valid_statuses}",
            )
        
        item = self.repo.create_item(
            category_id=category.category_id,
            serial_no=data.serial_no,
            status=data.status,
        )
        
        # 생성된 item에 category 정보 로드
        item = self.repo.get_item_by_id(item.item_id)
        
        return {
            "success": True,
            "message": "물품이 생성되었습니다.",
            "data": ItemResponse(
                item_id=item.item_id,
                category_id=item.category_id,
                category_name=item.category.category_name if item.category else "Unknown",
                serial_no=item.serial_no,
                status=item.status,
            ),
        }

    def update_item(self, item_id: int, data: ItemFullUpdate) -> dict:
        """물품 수정"""
        item = self.repo.get_item_by_id(item_id)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="물품을 찾을 수 없습니다.",
            )
        
        # 카테고리 존재 확인
        category_id_to_update = None
        if data.category_name is not None:
            category_name = data.category_name.lower()
            if category_name not in VALID_CATEGORY_NAMES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"카테고리 '{data.category_name}'을(를) 찾을 수 없습니다. (umbrella 또는 powerbank 사용)",
                )
            category = self.repo.get_category_by_name(category_name)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"카테고리 '{category_name}'이(가) DB에 존재하지 않습니다.",
                )
            category_id_to_update = category.category_id
        
        # 시리얼 번호 중복 체크
        if data.serial_no:
            existing = self.repo.get_item_by_serial_no(data.serial_no)
            if existing and existing.item_id != item_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"시리얼 번호 '{data.serial_no}'가 이미 존재합니다.",
                )
        
        # status 유효성 검사
        if data.status is not None:
            valid_statuses = ["AVAILABLE", "RENTED", "RESERVED", "BROKEN"]
            if data.status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"유효하지 않은 status입니다. 가능한 값: {valid_statuses}",
                )
        
        update_dict = {}
        if category_id_to_update is not None:
            update_dict["category_id"] = category_id_to_update
        if data.serial_no is not None:
            update_dict["serial_no"] = data.serial_no
        if data.status is not None:
            update_dict["status"] = data.status
        
        self.repo.update_item(item, update_dict)
        
        return {
            "success": True,
            "message": "물품이 수정되었습니다.",
        }

    def delete_item(self, item_id: int) -> dict:
        """물품 삭제"""
        item = self.repo.get_item_by_id(item_id)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="물품을 찾을 수 없습니다.",
            )
        
        self.repo.delete_item(item)
        
        return {
            "success": True,
            "message": "물품이 삭제되었습니다.",
        }

