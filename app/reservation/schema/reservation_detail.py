from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.personal.schema.personal import BooleanResponse


class ReservationItemInfo(BaseModel):
    item_id: int
    category_name: str
    cable: bool


class ReservationInfo(BaseModel):
    status: str
    pickup_on: datetime


class DepositInfo(BaseModel):
    deposit_paid: bool
    deposit_refunded: bool


class ReservationDetailData(BaseModel):
    reservation_id: int
    item: ReservationItemInfo
    reservation_info: ReservationInfo
    deposit: DepositInfo


class ReservationDetailResponse(BooleanResponse):
    data: ReservationDetailData
