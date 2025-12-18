from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.personal.schema.personal import BooleanResponse


class RentalItem(BaseModel):
    reservation_id: int
    rental_id: Optional[int] = None
    item_id: int
    category_name: str
    cable: bool
    rented_on: Optional[datetime] = None
    due_on: Optional[datetime] = None
    returned_on: Optional[datetime] = None
    status: str


class RentalResponse(BooleanResponse):
    data: List[RentalItem]

