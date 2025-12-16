from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    name: str
    department: str
    student_no: str
    phone: str
    password: str
    email: EmailStr
    account_bank: str
    account_num: str


class UserLogin(BaseModel):
    student_no: str
    password: str


class UserResponse(BaseModel):
    member_id: int
    student_no: str
    name: str
    department: str
    email: str
    is_admin: bool

    class Config:
        from_attributes = True


class RegisterResponse(BaseModel):
    success: bool
    message: str
    data: dict


class LoginResponse(BaseModel):
    success: bool
    message: str
    data: dict


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    student_no: Optional[str] = None

