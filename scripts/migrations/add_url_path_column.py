"""
URL 경로 컬럼 추가 마이그레이션
"""
import sys
import io
from app.database import engine
from sqlalchemy import text

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def add_url_path_column():
    """fortune_service_config 테이블에 url_path 컬럼 추가"""
    with engine.connect() as conn:
        # 컬럼이 이미 존재하는지 확인
        result = conn.execute(text("PRAGMA table_info(fortune_service_config)"))
        columns = [row[1] for row in result.fetchall()]

        if 'url_path' not in columns:
            print("url_path column adding...")
            conn.execute(text("ALTER TABLE fortune_service_config ADD COLUMN url_path VARCHAR(100)"))
            conn.commit()
            print("Done: url_path column added")

            # 기존 데이터에 기본 URL 경로 설정
            print("Setting default URL paths...")
            conn.execute(text("UPDATE fortune_service_config SET url_path = '/fortune/' || code WHERE url_path IS NULL"))
            conn.commit()
            print("Done: Default URL paths set")
        else:
            print("url_path column already exists")

if __name__ == "__main__":
    add_url_path_column()
