"""
관리자 인증 서비스
"""
from sqlalchemy.orm import Session
from app.models.admin_user import AdminUser
from app.utils.security import verify_password, get_password_hash
from typing import Optional


class AuthService:
    """관리자 인증 관리"""

    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> Optional[AdminUser]:
        """
        사용자 인증

        Args:
            username: 사용자명
            password: 비밀번호

        Returns:
            인증된 사용자 or None
        """
        user = self.db.query(AdminUser).filter(
            AdminUser.username == username
        ).first()

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    def create_admin_user(self, username: str, password: str) -> AdminUser:
        """
        관리자 계정 생성

        Args:
            username: 사용자명
            password: 비밀번호

        Returns:
            생성된 사용자
        """
        # 이미 있는지 확인
        existing = self.db.query(AdminUser).filter(
            AdminUser.username == username
        ).first()

        if existing:
            raise ValueError(f"이미 존재하는 사용자입니다: {username}")

        # 새 사용자 생성
        hashed_password = get_password_hash(password)
        new_user = AdminUser(
            username=username,
            password_hash=hashed_password
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user
