"""
요청/응답 로깅 미들웨어
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import Response
import time
from app.database import SessionLocal
from app.utils.logger import Logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """모든 요청/응답을 로깅하는 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        # 시작 시간 기록
        start_time = time.time()

        # 관리자 페이지, 정적 파일, API 상태 체크는 로깅 제외 (너무 많음)
        exclude_paths = ["/admin/", "/static/", "/favicon.ico", "/.well-known/", "/api/fortune/status/"]
        should_log = not any(request.url.path.startswith(path) for path in exclude_paths)

        # 응답 처리
        response = await call_next(request)

        # 응답 시간 계산
        response_time_ms = int((time.time() - start_time) * 1000)

        # 로깅 (비동기가 아닌 동기로 처리)
        if should_log:
            try:
                db = SessionLocal()
                logger = Logger(db)

                # 운세 요청인지 확인
                is_fortune_request = request.url.path.startswith("/fortune/") and request.method == "POST"
                service_code = None
                if is_fortune_request:
                    # URL에서 서비스 코드 추출 (/fortune/saju -> saju)
                    path_parts = request.url.path.split("/")
                    if len(path_parts) >= 3:
                        service_code = path_parts[2]

                logger.log_access(
                    url=str(request.url),
                    method=request.method,
                    status_code=response.status_code,
                    client_ip=request.client.host if request.client else "unknown",
                    user_agent=request.headers.get("user-agent"),
                    referer=request.headers.get("referer"),
                    response_time_ms=response_time_ms,
                    service_code=service_code,
                    is_fortune_request=is_fortune_request
                )

                db.close()
            except Exception as e:
                # 로깅 실패는 무시 (메인 기능에 영향 주지 않음)
                print(f"[WARNING] Logging failed: {e}")

        return response
