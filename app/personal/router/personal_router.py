from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.router.auth_router import get_current_user
from app.db.database import get_db
from app.personal.service.personal_service import PersonalService
from app.personal.schema.personal import BooleanResponse, PersonalInfoResponse, personalInfoUpdateRequest

router = APIRouter(prefix="/mypage", tags=["mypage"])


@router.get("/info", response_model=PersonalInfoResponse, summary="내 개인정보 조회")
def get_personal_info(
    student_no: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """JWT 토큰으로 인증된 사용자의 개인정보 조회"""
    personal_service = PersonalService(db)
    return personal_service.get_personal_info(student_no)

@router.patch("/info",response_model=BooleanResponse,summary="내 개인정보 수정")
def set_personal_info(
    request: personalInfoUpdateRequest,
    student_no: str=Depends(get_current_user),
    db : Session = Depends(get_db),
):
    personal_service=PersonalService(db)
    return personal_service.set_personal_info(student_no,request)