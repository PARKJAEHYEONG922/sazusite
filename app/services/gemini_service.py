"""
Gemini API 서비스
"""
import google.generativeai as genai
import time
import logging
from typing import Optional, Tuple, Dict
from app.config import get_settings

settings = get_settings()

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gemini_api.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GeminiService:
    """Gemini API 래퍼"""

    def __init__(self):
        """Gemini API 초기화"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        self.max_retries = 3
        self.retry_delay = 2  # 초

    def generate_content(self, prompt: str, service_code: Optional[str] = None, db=None, client_ip: Optional[str] = None) -> str:
        """
        Gemini API 호출하여 텍스트 생성 (재시도 로직 포함)

        Args:
            prompt: 입력 프롬프트
            service_code: 서비스 코드 (로깅용)
            db: DB 세션 (로깅용)
            client_ip: 클라이언트 IP (로깅용)

        Returns:
            생성된 텍스트
        """
        last_error = None
        start_time = time.time()

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[{service_code}] Gemini API 호출 시작 (시도 {attempt}/{self.max_retries})")

                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.8,
                        "top_k": 40,
                        "top_p": 0.95,
                        "max_output_tokens": 2048,
                    }
                )

                # 응답 검증
                if not response or not response.text:
                    raise Exception("AI 응답이 비어있습니다")

                logger.info(f"[{service_code}] Gemini API 호출 성공 (응답 길이: {len(response.text)}자)")

                # 응답 시간 계산
                response_time_ms = int((time.time() - start_time) * 1000)

                # API 사용 로깅 (DB가 있고 service_code가 있는 경우만)
                if db and service_code:
                    try:
                        from app.utils.logger import Logger
                        db_logger = Logger(db)

                        # 토큰 사용량 추출 (Gemini API response에서)
                        prompt_tokens = None
                        completion_tokens = None
                        total_tokens = None
                        estimated_cost = 0.0

                        if hasattr(response, 'usage_metadata'):
                            usage = response.usage_metadata
                            prompt_tokens = getattr(usage, 'prompt_token_count', None)
                            completion_tokens = getattr(usage, 'candidates_token_count', None)
                            total_tokens = getattr(usage, 'total_token_count', None)

                            # 비용 계산 (Gemini 2.0 Flash 기준)
                            # Input: $0.075 per 1M tokens
                            # Output: $0.30 per 1M tokens
                            if prompt_tokens and completion_tokens:
                                estimated_cost = (prompt_tokens * 0.075 / 1_000_000) + (completion_tokens * 0.30 / 1_000_000)

                        db_logger.log_api_usage(
                            model=settings.gemini_model,
                            service_code=service_code,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            total_tokens=total_tokens,
                            estimated_cost=estimated_cost,
                            response_time_ms=response_time_ms,
                            is_cached=False,
                            cache_hit=False,
                            client_ip=client_ip
                        )
                    except Exception as log_error:
                        # 로깅 실패는 무시 (메인 기능에 영향 주지 않음)
                        logger.warning(f"[{service_code}] API usage logging failed: {log_error}")

                return response.text

            except Exception as e:
                last_error = e
                error_msg = str(e)
                error_type = type(e).__name__

                # 마지막 시도가 아니면 재시도
                if attempt < self.max_retries:
                    logger.warning(
                        f"[{service_code}] Gemini API 호출 실패 (시도 {attempt}/{self.max_retries})\n"
                        f"  에러 타입: {error_type}\n"
                        f"  에러 메시지: {error_msg}\n"
                        f"  {self.retry_delay}초 후 재시도..."
                    )
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # 모든 재시도 실패
                    logger.error(
                        f"[{service_code}] Gemini API 호출 최종 실패 ({self.max_retries}회 시도)\n"
                        f"  에러 타입: {error_type}\n"
                        f"  에러 메시지: {error_msg}\n"
                        f"  클라이언트 IP: {client_ip}"
                    )

                    # DB에 에러 로깅
                    if db:
                        try:
                            from app.utils.logger import Logger
                            error_logger = Logger(db)
                            error_logger.log_error(
                                error_type=f"GeminiAPI_{error_type}",
                                error_message=f"[{service_code}] {error_msg}",
                                stack_trace=None,
                                url=None,
                                method="AI_GENERATE",
                                client_ip=client_ip,
                                user_agent=f"Gemini API ({service_code})"
                            )
                        except Exception as log_error:
                            logger.warning(f"에러 로깅 실패: {log_error}")

        # 모든 시도 실패 시
        final_error = Exception(
            f"AI 운세 생성에 실패했습니다. "
            f"({self.max_retries}회 시도 후 실패)\n"
            f"오류: {str(last_error)}"
        )
        logger.critical(f"[{service_code}] 최종 에러 발생: {final_error}")
        raise final_error


# 싱글톤 인스턴스
gemini_service = GeminiService()
