"""
Gemini API 서비스
"""
import google.generativeai as genai
from app.config import get_settings

settings = get_settings()


class GeminiService:
    """Gemini API 래퍼"""

    def __init__(self):
        """Gemini API 초기화"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    def generate_content(self, prompt: str) -> str:
        """
        Gemini API 호출하여 텍스트 생성

        Args:
            prompt: 입력 프롬프트

        Returns:
            생성된 텍스트
        """
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
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API 호출 실패: {str(e)}")


# 싱글톤 인스턴스
gemini_service = GeminiService()
