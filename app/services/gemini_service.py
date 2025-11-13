"""
Gemini API 서비스
"""
import google.generativeai as genai
import time
from app.config import get_settings

settings = get_settings()


class GeminiService:
    """Gemini API 래퍼"""

    def __init__(self):
        """Gemini API 초기화"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        self.max_retries = 3
        self.retry_delay = 2  # 초

    def generate_content(self, prompt: str) -> str:
        """
        Gemini API 호출하여 텍스트 생성 (재시도 로직 포함)

        Args:
            prompt: 입력 프롬프트

        Returns:
            생성된 텍스트
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
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

                return response.text

            except Exception as e:
                last_error = e
                error_msg = str(e)

                # 마지막 시도가 아니면 재시도
                if attempt < self.max_retries:
                    print(f"AI API 호출 실패 (시도 {attempt}/{self.max_retries}): {error_msg}")
                    print(f"{self.retry_delay}초 후 재시도...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # 모든 재시도 실패
                    print(f"AI API 호출 최종 실패 ({self.max_retries}회 시도): {error_msg}")

        # 모든 시도 실패 시
        raise Exception(
            f"AI 운세 생성에 실패했습니다. "
            f"({self.max_retries}회 시도 후 실패)\n"
            f"오류: {str(last_error)}"
        )


# 싱글톤 인스턴스
gemini_service = GeminiService()
