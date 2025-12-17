from re import S
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.auth.repository.user_repository import UserRepository
from app.personal.schema.personal import BooleanResponse, PersonalInfoResponse, PersonalInfoData, RefundAccount


class PersonalService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db=db
    
    def get_personal_info(self, student_no: str) -> PersonalInfoResponse:
        """개인정보 조회"""
        user = self.user_repo.get_by_student_no(student_no)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return PersonalInfoResponse(
            success=True,
            message="사용자 정보 조회 성공",
            data=PersonalInfoData(
                member_id=user.id,
                student_no=user.student_no,
                name=user.name,
                department=user.department,
                email=user.email,
                phone=user.phone,
                refund_account=RefundAccount(
                    account_bank=user.account_bank,
                    account_num=user.account_num
                )
            )
        )
    
    def set_personal_info(self,student_no:str,update_data)->dict:
        user=self.user_repo.get_by_student_no(student_no)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        for field, value in update_data:
            if value is not None:
                setattr(user,field,value)

        self.db.commit()

        return BooleanResponse(
            success=True,
            message="사용자 정보가 수정되었습니다."
        )


