"""
로깅 유틸리티
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import traceback
import time

from app.models.log import ErrorLog, APIUsageLog, AccessLog, RateLimitLog


class Logger:
    """통합 로거"""

    def __init__(self, db: Session):
        self.db = db

    def log_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        url: Optional[str] = None,
        method: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        service_code: Optional[str] = None,
        user_key: Optional[str] = None
    ):
        """에러 로그 기록"""
        error_log = ErrorLog(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            url=url,
            method=method,
            client_ip=client_ip,
            user_agent=user_agent,
            service_code=service_code,
            user_key=user_key
        )
        self.db.add(error_log)
        self.db.commit()

        # 콘솔에도 출력 (개발 환경)
        print(f"[ERROR] {error_type}: {error_message}")

    def log_api_usage(
        self,
        model: str,
        service_code: str,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        estimated_cost: Optional[float] = None,
        response_time_ms: Optional[int] = None,
        is_cached: bool = False,
        cache_hit: bool = False,
        client_ip: Optional[str] = None,
        user_key: Optional[str] = None
    ):
        """API 사용 로그 기록"""
        api_log = APIUsageLog(
            model=model,
            service_code=service_code,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            response_time_ms=response_time_ms,
            is_cached=is_cached,
            cache_hit=cache_hit,
            client_ip=client_ip,
            user_key=user_key
        )
        self.db.add(api_log)
        self.db.commit()

    def log_access(
        self,
        url: str,
        method: str,
        status_code: int,
        client_ip: str,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        service_code: Optional[str] = None,
        is_fortune_request: bool = False
    ):
        """접속 로그 기록"""
        access_log = AccessLog(
            url=url,
            method=method,
            status_code=status_code,
            client_ip=client_ip,
            user_agent=user_agent,
            referer=referer,
            response_time_ms=response_time_ms,
            service_code=service_code,
            is_fortune_request=is_fortune_request
        )
        self.db.add(access_log)
        self.db.commit()

    def log_rate_limit_violation(
        self,
        client_ip: str,
        limit_type: str,
        current_count: int,
        max_allowed: int,
        url: str,
        method: str,
        user_agent: Optional[str] = None
    ):
        """Rate Limit 위반 로그 기록"""
        rate_limit_log = RateLimitLog(
            client_ip=client_ip,
            limit_type=limit_type,
            current_count=current_count,
            max_allowed=max_allowed,
            url=url,
            method=method,
            user_agent=user_agent
        )
        self.db.add(rate_limit_log)
        self.db.commit()

        # 콘솔에도 출력
        print(f"[RATE LIMIT] IP {client_ip} exceeded {limit_type} limit: {current_count}/{max_allowed}")


def log_exception(db: Session, exception: Exception, request=None, service_code: Optional[str] = None):
    """
    예외 발생 시 자동 로깅 (헬퍼 함수)

    Usage:
        try:
            # some code
        except Exception as e:
            log_exception(db, e, request, service_code="saju")
            raise
    """
    logger = Logger(db)

    error_type = type(exception).__name__
    error_message = str(exception)
    stack_trace = traceback.format_exc()

    url = None
    method = None
    client_ip = None
    user_agent = None

    if request:
        url = str(request.url)
        method = request.method
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    logger.log_error(
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        url=url,
        method=method,
        client_ip=client_ip,
        user_agent=user_agent,
        service_code=service_code
    )


class APIUsageTracker:
    """API 사용량 추적 컨텍스트 매니저"""

    def __init__(self, db: Session, model: str, service_code: str, client_ip: Optional[str] = None):
        self.db = db
        self.model = model
        self.service_code = service_code
        self.client_ip = client_ip
        self.start_time = None
        self.logger = Logger(db)

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            response_time_ms = int((time.time() - self.start_time) * 1000)
        else:
            response_time_ms = None

        # API 사용 로그 기록 (성공/실패 관계없이)
        # 실제 토큰 수는 나중에 업데이트 가능
        self.logger.log_api_usage(
            model=self.model,
            service_code=self.service_code,
            response_time_ms=response_time_ms,
            client_ip=self.client_ip
        )

        return False  # 예외를 다시 발생시킴
