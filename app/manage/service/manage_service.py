from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.manage.repository.manage_repository import ManageRepository
from app.manage.schema.manage import (
    UserRentalItem,
    UserRentalStatusUpdate,
    ItemResponse,
    ItemUpdate,
    MemberInfo,
    ItemInfo,
    TimelineInfo,
    RefundAccountInfo,
)


class ManageService:
    def __init__(self, db: Session):
        self.repo = ManageRepository(db)

    # ==================== 1. 학생 대여 목록 조회 ====================

    def get_all_user_rentals(self) -> dict:
        """
        모든 학생의 대여 정보 조회 (예약 기준)
        - reservation_id가 있고 rental_id가 없으면 → 예약중
        - rental_id가 있고 returned_on이 없으면 → 대여중
        - returned_on이 있으면 → 환급전
        """
        reservations = self.repo.get_all_reservations_with_details()
        
        result = []
        for reservation in reservations:
            # 회원 정보
            member = reservation.member
            member_info = MemberInfo(
                member_id=member.member_id,
                name=member.name,
                student_no=member.student_no,
            )
            
            # 물품 정보
            item = reservation.item
            category_name = item.category.category_name if item.category else "Unknown"
            item_info = ItemInfo(
                item_id=item.item_id,
                category_name=category_name,
                cable=reservation.cable,
            )
            
            # 대여 정보 (rental)
            rental = None
            if hasattr(reservation, 'rental') and reservation.rental:
                # rental이 리스트가 아니라 단일 객체인 경우
                if isinstance(reservation.rental, list):
                    rental = reservation.rental[0] if reservation.rental else None
                else:
                    rental = reservation.rental
            
            # 타임라인 정보
            timeline_info = TimelineInfo(
                pickup_on=reservation.pickup_on,
                rented_on=rental.rented_on if rental else None,
                due_on=rental.due_on if rental else None,
                returned_on=rental.returned_on if rental else None,
            )
            
            # 상태 결정
            if rental is None:
                rental_status = "예약중"
            elif rental.returned_on is None:
                rental_status = "대여중"
            else:
                rental_status = "환급전"
            
            # 환불 계좌 정보
            bank_account = self.repo.get_bank_account_by_member_id(member.member_id)
            if bank_account:
                refund_account = RefundAccountInfo(
                    account_bank=bank_account.account_bank,
                    account_num=bank_account.account_num,
                )
            else:
                # User 모델에 있는 계좌 정보 사용 (fallback)
                refund_account = RefundAccountInfo(
                    account_bank=member.account_bank if hasattr(member, 'account_bank') else "",
                    account_num=member.account_num if hasattr(member, 'account_num') else "",
                )
            
            result.append(UserRentalItem(
                reservation_id=reservation.reservation_id,
                rental_id=rental.rental_id if rental else None,
                member=member_info,
                item=item_info,
                timeline=timeline_info,
                status=rental_status,
                refund_account=refund_account,
            ))
        
        return {
            "success": True,
            "message": "학생 대여 목록 조회 성공",
            "data": result,
        }

    # ==================== 2. 학생 대여 목록 수정 ====================

    def update_user_rental_status(self, user_id: int, update_data: UserRentalStatusUpdate) -> dict:
        """
        학생 대여 상태 수정
        
        status에 따른 동작:
        - "대여중": createRental() - 예약 → 대여 시작
        - "반납완료": setReturnedOn() - 반납 처리
        - "환급완료": setDepositRefunded() - 환급 처리
        - "예약취소": cancelReservation() - 예약 취소
        """
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # reservation_id가 있으면 해당 예약 사용, 없으면 사용자의 최근 예약 사용
        if update_data.reservation_id:
            reservation = self.repo.get_reservation_by_id(update_data.reservation_id)
            if not reservation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reservation not found",
                )
            if reservation.member_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reservation does not belong to this user",
                )
        else:
            # 사용자의 예약 목록에서 처리 가능한 예약 찾기
            reservations = self.repo.get_reservations_by_member_id(user_id)
            if not reservations:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No reservation found for this user",
                )
            reservation = reservations[0]  # 가장 최근 예약

        # status에 따른 동작 수행
        new_status = update_data.status
        
        if new_status == "대여중":
            # 예약 → 대여 시작
            existing_rental = self.repo.get_rental_by_reservation_id(reservation.reservation_id)
            if existing_rental:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 대여 중인 예약입니다.",
                )
            self.repo.create_rental(reservation)
            message = "대여가 시작되었습니다."
            
        elif new_status == "반납완료":
            # 반납 처리
            rental = self.repo.get_rental_by_reservation_id(reservation.reservation_id)
            if not rental:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="대여 정보가 없습니다. 먼저 대여를 시작해주세요.",
                )
            if rental.returned_on:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 반납 완료된 대여입니다.",
                )
            self.repo.set_returned_on(rental)
            message = "반납이 완료되었습니다."
            
        elif new_status == "환급완료":
            # 환급 처리
            rental = self.repo.get_rental_by_reservation_id(reservation.reservation_id)
            if not rental or not rental.returned_on:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="반납이 완료되지 않은 대여입니다.",
                )
            # 보증금 환급 기록
            item = self.repo.get_item_by_id(reservation.item_id)
            deposit_amount = item.category.deposit_required if item and item.category else 0
            if deposit_amount > 0:
                self.repo.create_deposit_refund(
                    member_id=user_id,
                    item_id=reservation.item_id,
                    amount=deposit_amount,
                )
            message = "환급이 완료되었습니다."
            
        elif new_status == "예약취소":
            # 예약 취소
            rental = self.repo.get_rental_by_reservation_id(reservation.reservation_id)
            if rental:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 대여가 시작된 예약은 취소할 수 없습니다.",
                )
            self.repo.update_reservation_status(reservation, "CANCELLED")
            
            # 물품 상태 복구
            item = self.repo.get_item_by_id(reservation.item_id)
            if item:
                self.repo.update_item(item, {"status": "AVAILABLE"})
            message = "예약이 취소되었습니다."
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 상태 변경: {new_status}",
            )
        
        return {
            "success": True,
            "message": "대여 상태가 수정되었습니다.",
        }

    # ==================== 3. 학생 예약/대여 정보 삭제 ====================

    def delete_user_rentals(self, user_id: int) -> dict:
        """학생의 예약/대여 정보 삭제"""
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # 해당 사용자의 모든 예약/대여 정보 삭제
        self.repo.delete_user_reservations_and_rentals(user_id)
        
        return {
            "success": True,
            "message": "학생 예약/대여 정보 삭제 성공",
        }

    # ==================== 4. 재고 목록 조회 ====================

    @staticmethod
    def _convert_item_status_to_korean(status: str) -> str:
        """item status를 한글로 변환"""
        status_map = {
            "AVAILABLE": "사용가능",
            "RENTED": "대여중",
            "RETURNED": "반납완료",
            "BROKEN": "분실 및 고장",
            "RESERVED": "예약중",
        }
        return status_map.get(status, status)

    def get_all_items(self) -> dict:
        """모든 재고 조회"""
        items = self.repo.get_all_items()
        
        result = []
        for item in items:
            category_name = "Unknown"
            if item.category:
                category_name = item.category.category_name
            
            result.append(ItemResponse(
                item_id=item.item_id,
                category_name=category_name,
                serial_no=item.serial_no,
                status=self._convert_item_status_to_korean(item.status),
            ))
        
        return {
            "success": True,
            "message": "재고 조회 성공",
            "data": result,
        }

    # ==================== 5. 재고 수정 ====================

    @staticmethod
    def _convert_item_status_to_english(status_kr: str) -> str:
        """한글 status를 영문 DB 값으로 변환"""
        status_map = {
            "사용가능": "AVAILABLE",
            "대여중": "RENTED",
            "반납완료": "RETURNED",
            "분실 및 고장": "BROKEN",
            "예약중": "RESERVED",
        }
        return status_map.get(status_kr, status_kr)

    def update_item(self, item_id: int, update_data: ItemUpdate) -> dict:
        """재고 정보 수정"""
        item = self.repo.get_item_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
        
        # 한글 status를 영문으로 변환
        valid_statuses_kr = ["사용가능", "대여중", "반납완료", "분실 및 고장", "예약중"]
        if update_data.status not in valid_statuses_kr:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {valid_statuses_kr}",
            )
        
        db_status = self._convert_item_status_to_english(update_data.status)
        self.repo.update_item(item, {"status": db_status})
        
        return {
            "success": True,
            "message": "재고 상태가 수정되었습니다.",
        }

    # ==================== 6. 재고 삭제 ====================

    def delete_item(self, item_id: int) -> dict:
        """재고 삭제"""
        item = self.repo.get_item_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
        
        self.repo.delete_item(item)
        
        return {
            "success": True,
            "message": "재고 삭제 성공",
        }
