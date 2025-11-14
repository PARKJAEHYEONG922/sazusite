"""
데이터베이스 연결 설정
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# SQLite 연결 (초기)
# 배포 시 PostgreSQL로 변경: settings.database_url 사용
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """DB 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """모든 테이블 생성"""
    # 모델 import (테이블 생성을 위해)
    from app.models import admin_user, fortune_result, site_config, service_config
    from app.models.log import ErrorLog, APIUsageLog, AccessLog, RateLimitLog

    Base.metadata.create_all(bind=engine)
