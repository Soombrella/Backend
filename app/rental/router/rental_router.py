from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.router.auth_router import get_current_user
from app.db.database import get_db
from app.rental.schema.rental import RentalResponse
from app.rental.service.rental_service import RentalService

router = APIRouter(prefix="/mypage", tags=["mypage"])


@router.get(
    "/rentals",
    response_model=RentalResponse,
    summary="대여 이력 조회",
)
def get_personal_info(
    student_no: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = RentalService(db)
    return service.get_rental_info(student_no)
