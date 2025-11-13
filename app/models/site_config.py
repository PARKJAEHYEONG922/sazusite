"""
사이트 전체 설정 모델
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SiteConfig(Base):
    """사이트 전체 설정"""
    __tablename__ = "site_config"

    id = Column(Integer, primary_key=True, index=True)

    # 기본 정보
    site_name = Column(String(100), default="명월헌")
    main_title = Column(String(200), default="명월헌 – 야광묘가 알려주는 오늘의 기운")
    main_subtitle = Column(Text, default="전통 운세와 AI가 만나 더욱 정확한 운세를 알려드립니다")

    # 이미지
    hero_image_url = Column(String(500), nullable=True)

    # 빠른 운세
    quick_fortune_title = Column(String(100), default="빠른 운세 보기")
    quick_fortune_description = Column(Text, default="간단한 정보 입력으로 바로 확인하세요")

    # 푸터
    footer_text = Column(Text, default="© 2025 명월헌(明月軒). All rights reserved.")

    # 애드센스
    adsense_client_id = Column(String(100), nullable=True)
    adsense_slot_main = Column(String(100), nullable=True)
    adsense_slot_result = Column(String(100), nullable=True)

    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
