from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.personal.schema.personal import BooleanResponse


class RentalItemInfo(BaseModel):
    item_id: int
    category_name: str
    cable: bool


class RentalInfo(BaseModel):
    status: str
    rented_on: datetime
    due_on: datetime
    returned_on: Optional[datetime]
    proxy_return: bool


class DepositInfo(BaseModel):
    deposit_paid: bool
    deposit_refunded: bool


class RentalDetailData(BaseModel):
    rental_id: int
    reservation_id: int
    item: RentalItemInfo
    rental_info: RentalInfo
    deposit: DepositInfo


class RentalDetailResponse(BooleanResponse):
    data: RentalDetailData
