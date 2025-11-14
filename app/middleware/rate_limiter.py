"""
Rate Limiting 미들웨어 - API 남용 방지
"""
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from typing import Dict, List
import asyncio


class RateLimiter:
    """IP 기반 Rate Limiting"""

    def __init__(
        self,
        per_minute: int = 5,
        per_day: int = 20
    ):
        """
        Args:
            per_minute: 1분당 최대 요청 수
            per_day: 하루 최대 요청 수
        """
        self.per_minute = per_minute
        self.per_day = per_day

        # IP별 요청 기록
        self.minute_requests: Dict[str, List[datetime]] = defaultdict(list)
        self.day_requests: Dict[str, List[datetime]] = defaultdict(list)

        # 주기적으로 오래된 기록 정리
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """오래된 요청 기록 정리 (메모리 절약)"""
        async def cleanup():
            while True:
                await asyncio.sleep(600)  # 10분마다 정리
                now = datetime.now()

                # 1분 이상 지난 기록 삭제
                for ip in list(self.minute_requests.keys()):
                    self.minute_requests[ip] = [
                        ts for ts in self.minute_requests[ip]
                        if now - ts < timedelta(minutes=2)
                    ]
                    if not self.minute_requests[ip]:
                        del self.minute_requests[ip]

                # 1일 이상 지난 기록 삭제
                for ip in list(self.day_requests.keys()):
                    self.day_requests[ip] = [
                        ts for ts in self.day_requests[ip]
                        if now - ts < timedelta(days=2)
                    ]
                    if not self.day_requests[ip]:
                        del self.day_requests[ip]

        asyncio.create_task(cleanup())

    def check_rate_limit(self, request: Request, db=None) -> None:
        """
        Rate Limit 검사

        Args:
            request: FastAPI Request 객체
            db: 데이터베이스 세션 (로깅용, 선택사항)

        Raises:
            HTTPException: Rate Limit 초과 시 429 에러
        """
        client_ip = request.client.host
        now = datetime.now()

        # 1분 제한 체크
        one_minute_ago = now - timedelta(minutes=1)
        self.minute_requests[client_ip] = [
            ts for ts in self.minute_requests[client_ip]
            if ts > one_minute_ago
        ]

        if len(self.minute_requests[client_ip]) >= self.per_minute:
            # 위반 로그 기록
            if db:
                try:
                    from app.utils.logger import Logger
                    logger = Logger(db)
                    logger.log_rate_limit_violation(
                        client_ip=client_ip,
                        limit_type="minute",
                        current_count=len(self.minute_requests[client_ip]),
                        max_allowed=self.per_minute,
                        url=str(request.url),
                        method=request.method,
                        user_agent=request.headers.get("user-agent")
                    )
                except Exception:
                    pass  # 로깅 실패해도 Rate Limit은 작동

            raise HTTPException(
                status_code=429,
                detail=f"요청 횟수 제한: 1분에 최대 {self.per_minute}회까지만 가능합니다. 잠시 후 다시 시도해주세요."
            )

        # 하루 제한 체크
        one_day_ago = now - timedelta(days=1)
        self.day_requests[client_ip] = [
            ts for ts in self.day_requests[client_ip]
            if ts > one_day_ago
        ]

        if len(self.day_requests[client_ip]) >= self.per_day:
            # 위반 로그 기록
            if db:
                try:
                    from app.utils.logger import Logger
                    logger = Logger(db)
                    logger.log_rate_limit_violation(
                        client_ip=client_ip,
                        limit_type="day",
                        current_count=len(self.day_requests[client_ip]),
                        max_allowed=self.per_day,
                        url=str(request.url),
                        method=request.method,
                        user_agent=request.headers.get("user-agent")
                    )
                except Exception:
                    pass

            raise HTTPException(
                status_code=429,
                detail=f"일일 요청 횟수 제한: 하루 최대 {self.per_day}회까지만 가능합니다. 내일 다시 이용해주세요."
            )

        # 요청 기록
        self.minute_requests[client_ip].append(now)
        self.day_requests[client_ip].append(now)

    def get_remaining_requests(self, request: Request) -> dict:
        """
        남은 요청 횟수 조회 (디버깅/모니터링용)

        Args:
            request: FastAPI Request 객체

        Returns:
            남은 요청 횟수 정보
        """
        client_ip = request.client.host
        now = datetime.now()

        # 1분 내 요청 수
        one_minute_ago = now - timedelta(minutes=1)
        minute_count = len([
            ts for ts in self.minute_requests.get(client_ip, [])
            if ts > one_minute_ago
        ])

        # 하루 내 요청 수
        one_day_ago = now - timedelta(days=1)
        day_count = len([
            ts for ts in self.day_requests.get(client_ip, [])
            if ts > one_day_ago
        ])

        return {
            "minute_remaining": self.per_minute - minute_count,
            "day_remaining": self.per_day - day_count,
            "minute_total": self.per_minute,
            "day_total": self.per_day
        }


# 전역 Rate Limiter 인스턴스
rate_limiter = RateLimiter(per_minute=5, per_day=20)
