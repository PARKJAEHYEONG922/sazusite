"""
명월헌 환경 설정
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """환경 변수 설정"""

    # 데이터베이스
    database_url: str = "sqlite:///./myeongwolheon.db"

    # 보안
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24시간

    # 관리자 초기 계정
    admin_username: str = "admin"
    admin_password: str = "admin123!"

    # Gemini API
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"
    gemini_api_url: str = "https://generativelanguage.googleapis.com/v1beta/models"

    # 환경
    environment: str = "development"
    debug: bool = True

    # 캐시
    cache_enabled: bool = True
    cache_duration_hours: int = 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        """설정 초기화 및 프로덕션 환경 검증"""
        super().__init__(**kwargs)

        # 프로덕션 환경에서 보안 검증
        if self.environment == "production":
            self._validate_production_settings()

    def _validate_production_settings(self):
        """프로덕션 환경 필수 설정 검증"""
        errors = []

        # SECRET_KEY 검증
        if self.secret_key == "change-this-secret-key-in-production":
            errors.append("❌ SECRET_KEY를 반드시 변경해야 합니다!")
        elif len(self.secret_key) < 32:
            errors.append("❌ SECRET_KEY는 최소 32자 이상이어야 합니다!")

        # 관리자 비밀번호 검증
        if self.admin_password == "admin123!":
            errors.append("❌ 관리자 비밀번호를 반드시 변경해야 합니다!")
        elif len(self.admin_password) < 12:
            errors.append("❌ 관리자 비밀번호는 최소 12자 이상이어야 합니다!")

        # Gemini API 키 검증
        if not self.gemini_api_key or self.gemini_api_key == "your-gemini-api-key-here":
            errors.append("❌ GEMINI_API_KEY를 설정해야 합니다!")

        # DEBUG 모드 검증
        if self.debug:
            errors.append("⚠️  경고: DEBUG=True는 보안 위험이 있습니다. DEBUG=False로 변경하세요!")

        # SQLite 사용 경고
        if "sqlite" in self.database_url.lower():
            errors.append("⚠️  경고: 프로덕션에서는 PostgreSQL 사용을 강력히 권장합니다!")

        # 에러가 있으면 예외 발생
        if errors:
            error_message = "\n".join([
                "",
                "=" * 60,
                "🚨 프로덕션 환경 설정 오류",
                "=" * 60,
                *errors,
                "=" * 60,
                "📝 .env 파일을 확인하고 위 항목들을 수정해주세요.",
                ""
            ])
            raise ValueError(error_message)

    def is_production(self) -> bool:
        """프로덕션 환경 여부 확인"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """개발 환경 여부 확인"""
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 반환"""
    return Settings()
