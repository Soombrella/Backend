from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.auth.router.auth_router import get_current_user
from app.reservation.service.reservation_service import ReservationService
from app.reservation.schema.reservation_detail import ReservationDetailResponse

router = APIRouter(prefix="/mypage", tags=["mypage"])


@router.get(
    "/reservations/{reservation_id}",
    response_model=ReservationDetailResponse,
    summary="세부 예약 이력 조회",
)
def get_reservation_detail(
    reservation_id: int,
    student_no: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ReservationService(db)
    return service.get_reservation_detail(reservation_id, student_no)
