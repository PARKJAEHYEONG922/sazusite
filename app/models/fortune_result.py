"""
운세 결과 캐시/로그 모델
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class FortuneResult(Base):
    """운세 결과 캐시 및 로그"""
    __tablename__ = "fortune_result"

    id = Column(Integer, primary_key=True, index=True)

    # 서비스 정보
    service_code = Column(String(20), index=True)  # today, saju, match, dream

    # 사용자 식별
    user_key = Column(String(64), index=True)  # SHA256 해시

    # 공유용 랜덤 코드 (URL에 사용)
    share_code = Column(String(12), unique=True, index=True, nullable=False)  # 예: xK9mP2wQ

    # 날짜
    date = Column(Date, index=True)  # 운세 기준 날짜

    # 요청/응답
    request_payload = Column(JSON)  # 입력 정보 (이름, 생년월일, 성별 등)
    result_text = Column(Text)  # 운세 결과 전체 텍스트

    # 캐시 여부
    is_from_cache = Column(Boolean, default=False)

    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 인덱스: 한 사람/한 서비스/하루에 하나만
    __table_args__ = (
        UniqueConstraint('service_code', 'user_key', 'date', name='uix_service_user_date'),
    )
