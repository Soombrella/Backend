from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.rental.repository.rental_repository import RentalRepository
from app.rental.schema.rental import RentalResponse, RentalItem
from app.rental.schema.rental_detail import DepositInfo, RentalDetailData, RentalDetailResponse, RentalInfo, RentalItemInfo


class RentalService:
    def __init__(self, db: Session):
        self.rental_repo = RentalRepository(db)

    def get_rental_info(self, student_no: str) -> RentalResponse:
        rows = self.rental_repo.get_by_student_no(student_no)

        result = []

        now = datetime.now()

        for reservation, rental, item, category in rows:
            if rental is None:
                status = "예약중"
            elif rental.returned_on is not None:
                status = "반납완료"
            elif rental.due_on < now:
                status = "연체중"
            else:
                status = "대여중"

            result.append(
                RentalItem(
                    reservation_id=reservation.reservation_id,
                    rental_id=rental.rental_id if rental else None,
                    item_id=item.item_id,
                    category_name=category.category_name,
                    cable=rental.cable if rental else False,

                    rented_on=rental.rented_on if rental else None,
                    due_on=rental.due_on if rental else None,
                    returned_on=rental.returned_on if rental else None,

                    status=status,
                )
            )

        return RentalResponse(
            success=True,
            message="대여 이력 조회 성공",
            data=result,
        )
    
    def get_rental_detail(self, rental_id: int, student_no: str) -> RentalDetailResponse:
        rental = self.rental_repo.get_rental_detail(rental_id)

        if not rental:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rental not found",
            )

        # 본인 대여만 조회 가능
        if rental.member.student_no != student_no:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )

        now = datetime.now()

        if rental.returned_on:
            status_str = "RETURNED"
        elif rental.due_on < now:
            status_str = "OVERDUE"
        else:
            status_str = "RENTED"

        deposit_paid = self.rental_repo.has_deposit(
            rental.member_id, rental.item_id
        )
        deposit_refunded = self.rental_repo.has_refund(
            rental.member_id, rental.item_id
        )

        return RentalDetailResponse(
            success=True,
            message="세부 대여 이력 조회 성공",
            data=RentalDetailData(
                rental_id=rental.rental_id,
                reservation_id=rental.reservation_id,
                item=RentalItemInfo(
                    item_id=rental.item.item_id,
                    category_name=rental.item.category.category_name,
                    cable=rental.cable,
                ),
                rental_info=RentalInfo(
                    status=status_str,
                    rented_on=rental.rented_on,
                    due_on=rental.due_on,
                    returned_on=rental.returned_on,
                    proxy_return=False,  # 추후 컬럼 생기면 연결
                ),
                deposit=DepositInfo(
                    deposit_paid=deposit_paid,
                    deposit_refunded=deposit_refunded,
                ),
            ),
        )
