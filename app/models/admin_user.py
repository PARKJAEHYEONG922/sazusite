"""
관리자 계정 모델
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class AdminUser(Base):
    """관리자 계정"""
    __tablename__ = "admin_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(200))  # bcrypt 해시

    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
