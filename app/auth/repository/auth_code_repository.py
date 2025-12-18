from sqlalchemy.orm import Session
from app.auth.model.auth_code import AuthCode
from typing import Optional
from datetime import datetime

class AuthCodeRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, member_id: int, email: str, code_hash: str, expires_at: datetime) -> AuthCode:
        """인증코드 생성 (기존 코드가 있으면 업데이트)"""
        # 기존 코드가 있으면 삭제
        existing = self.db.query(AuthCode).filter(AuthCode.member_id == member_id).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()
        
        db_auth_code = AuthCode(
            member_id=member_id,
            email=email,
            code_hash=code_hash,
            expires_at=expires_at
        )
        self.db.add(db_auth_code)
        self.db.commit()
        self.db.refresh(db_auth_code)
        return db_auth_code
    
    def get_by_email(self, email: str) -> Optional[AuthCode]:
        """이메일로 인증코드 조회"""
        return self.db.query(AuthCode).filter(AuthCode.email == email).first()
    
    def verify_code(self, email: str, code: str) -> bool:
        """인증코드 검증 (만료시간 체크 포함)"""
        auth_code = self.get_by_email(email)
        if not auth_code:
            return False
        
        # 코드 일치 확인
        if auth_code.code_hash != code:
            return False
        
        # 만료시간 확인
        if datetime.now(auth_code.expires_at.tzinfo) > auth_code.expires_at:
            return False
        
        return True
    
    def delete_by_email(self, email: str):
        """이메일로 인증코드 삭제"""
        auth_code = self.get_by_email(email)
        if auth_code:
            self.db.delete(auth_code)
            self.db.commit()
