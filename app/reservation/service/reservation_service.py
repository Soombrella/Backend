from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.reservation.repository.reservation_repository import ReservationRepository
from app.reservation.schema.reservation_detail import (
    ReservationDetailResponse,
    ReservationDetailData,
    ReservationItemInfo,
    ReservationInfo,
    DepositInfo,
)


class ReservationService:
    def __init__(self, db: Session):
        self.repo = ReservationRepository(db)

    def get_reservation_detail(
        self, reservation_id: int, student_no: str
    ) -> ReservationDetailResponse:
        row = self.repo.get_reservation_detail(reservation_id, student_no)

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found",
            )

        reservation, item, category = row

        deposit_paid = self.repo.has_deposit(
            reservation.member_id, reservation.item_id
        )
        deposit_refunded = self.repo.has_refund(
            reservation.member_id, reservation.item_id
        )

        return ReservationDetailResponse(
            success=True,
            message="세부 예약 이력 조회 성공",
            data=ReservationDetailData(
                reservation_id=reservation.reservation_id,
                item=ReservationItemInfo(
                    item_id=item.item_id,
                    category_name=category.category_name,
                    cable=reservation.cable,
                ),
                reservation_info=ReservationInfo(
                    status=reservation.status,
                    pickup_on=reservation.pickup_on,
                ),
                deposit=DepositInfo(
                    deposit_paid=deposit_paid,
                    deposit_refunded=deposit_refunded,
                ),
            ),
        )
