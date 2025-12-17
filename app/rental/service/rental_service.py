from datetime import datetime

from sqlalchemy.orm import Session
from app.rental.repository.rental_repository import RentalRepository
from app.rental.schema.rental import RentalResponse, RentalItem


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
