"""
로깅 관련 데이터베이스 모델
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from datetime import datetime
from app.database import Base


class ErrorLog(Base):
    """에러 로그"""
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)

    # 에러 정보
    error_type = Column(String(100))  # ValueError, HTTPException 등
    error_message = Column(Text)
    stack_trace = Column(Text, nullable=True)

    # 요청 정보
    url = Column(String(500), nullable=True)
    method = Column(String(10), nullable=True)  # GET, POST 등
    client_ip = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # 추가 컨텍스트
    service_code = Column(String(50), nullable=True)
    user_key = Column(String(100), nullable=True)
    is_resolved = Column(Boolean, default=False)


class APIUsageLog(Base):
    """API 사용 로그 (Gemini API)"""
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)

    # API 정보
    api_provider = Column(String(50), default="gemini")  # 확장 가능
    model = Column(String(100))  # gemini-2.0-flash-exp 등
    service_code = Column(String(50))  # today, saju, newyear2026 등

    # 사용량
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)

    # 비용 (추정치)
    estimated_cost = Column(Float, nullable=True)

    # 성능
    response_time_ms = Column(Integer, nullable=True)

    # 캐시 여부
    is_cached = Column(Boolean, default=False)
    cache_hit = Column(Boolean, default=False)

    # 요청 정보
    client_ip = Column(String(50), nullable=True)
    user_key = Column(String(100), nullable=True)


class AccessLog(Base):
    """사용자 접속 로그"""
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)

    # 요청 정보
    url = Column(String(500))
    method = Column(String(10))
    status_code = Column(Integer)

    # 클라이언트 정보
    client_ip = Column(String(50))
    user_agent = Column(String(500), nullable=True)
    referer = Column(String(500), nullable=True)

    # 성능
    response_time_ms = Column(Integer, nullable=True)

    # 서비스 정보
    service_code = Column(String(50), nullable=True)
    is_fortune_request = Column(Boolean, default=False)


class RateLimitLog(Base):
    """Rate Limit 위반 로그"""
    __tablename__ = "rate_limit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)

    # 클라이언트 정보
    client_ip = Column(String(50), index=True)
    user_agent = Column(String(500), nullable=True)

    # 위반 정보
    limit_type = Column(String(20))  # minute, day
    current_count = Column(Integer)
    max_allowed = Column(Integer)

    # 요청 정보
    url = Column(String(500))
    method = Column(String(10))
