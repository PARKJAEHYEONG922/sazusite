"""
운세 서비스 설정 모델
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class FortuneServiceConfig(Base):
    """4가지 운세 서비스 설정"""
    __tablename__ = "fortune_service_config"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True)  # today, saju, match, dream

    # 기본 정보
    title = Column(String(100))  # "오늘의 운세"
    subtitle = Column(String(200))  # "야광묘가 알려드려요"
    description = Column(Text)  # "행운의 색상·숫자·방향"

    # 캐릭터
    character_name = Column(String(50))  # "야광묘"
    character_emoji = Column(String(20))  # "🐱✨"

    # 활성화
    is_active = Column(Boolean, default=True)

    # AI 프롬프트 템플릿
    prompt_template = Column(Text, nullable=True)

    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
