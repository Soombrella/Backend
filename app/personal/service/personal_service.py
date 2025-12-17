from re import S
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.auth.repository.user_repository import UserRepository
from app.manage.model.bank_account import BankAccount
from app.manage.repository.manage_repository import ManageRepository
from app.personal.schema.personal import BooleanResponse, PersonalInfoResponse, PersonalInfoData, RefundAccount


class PersonalService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.bank_respo = ManageRepository(db)
        self.db=db
    
    def get_personal_info(self, student_no: str) -> PersonalInfoResponse:
        """개인정보 조회"""
        user = self.user_repo.get_by_student_no(student_no)
        bank=self.bank_respo.get_bank_account_by_member_id(user.member_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return PersonalInfoResponse(
            success=True,
            message="사용자 정보 조회 성공",
            data=PersonalInfoData(
                member_id=user.member_id,
                student_no=user.student_no,
                name=user.name,
                department=user.department,
                email=user.email,
                phone=user.phone,
                refund_account=RefundAccount(
                    account_bank=bank.account_bank,
                    account_num=bank.account_num
                )
            )
        )
    
    def set_personal_info(self,student_no:str,update_data)->dict:
        user=self.user_repo.get_by_student_no(student_no)
        bank=self.bank_respo.get_bank_account_by_member_id(user.member_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        for field, value in update_data:
            if value is not None:
                setattr(user,field,value)
        self.db.commit()

        # 🔹 기존 계좌 조회
        bank = self.bank_respo.get_bank_account_by_member_id(user.member_id)

        # 🔹 계좌가 없으면 생성
        if not bank:
            bank = BankAccount(
                member_id=user.member_id,
                account_bank=update_data.account_bank,
                account_num=update_data.account_num
            )
            self.db.add(bank)
        else:
            # 🔹 계좌가 있으면 수정
            if update_data.account_bank is not None:
                bank.account_bank = update_data.account_bank

            if update_data.account_num is not None:
                bank.account_num = update_data.account_num

            self.db.commit()

        return BooleanResponse(
            success=True,
            message="사용자 정보가 수정되었습니다."
        )


