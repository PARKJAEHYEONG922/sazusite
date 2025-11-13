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


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 반환"""
    return Settings()
