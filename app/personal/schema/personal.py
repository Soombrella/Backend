from typing import Optional
from pydantic import BaseModel


class RefundAccount(BaseModel):
    account_bank: str
    account_num: str


class PersonalInfoData(BaseModel):
    member_id: int
    student_no: str
    name: str
    department: str
    email: str
    phone: str
    refund_account: RefundAccount


class PersonalInfoResponse(BaseModel):
    success: bool
    message: str
    data: PersonalInfoData

class personalInfoUpdateRequest(BaseModel):
    email:Optional[str]=None
    department:Optional[str]=None
    account_bank:Optional[str]=None
    account_num:Optional[str]=None

class BooleanResponse(BaseModel):
    success: bool
    message: str