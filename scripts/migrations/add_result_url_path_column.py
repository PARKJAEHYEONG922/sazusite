"""
결과 페이지 URL 경로 컬럼 추가 마이그레이션
"""
import sys
import io
from app.database import engine
from sqlalchemy import text

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def add_result_url_path_column():
    """fortune_service_config 테이블에 result_url_path 컬럼 추가"""
    with engine.connect() as conn:
        # 컬럼이 이미 존재하는지 확인
        result = conn.execute(text("PRAGMA table_info(fortune_service_config)"))
        columns = [row[1] for row in result.fetchall()]

        if 'result_url_path' not in columns:
            print("result_url_path column adding...")
            conn.execute(text("ALTER TABLE fortune_service_config ADD COLUMN result_url_path VARCHAR(100)"))
            conn.commit()
            print("Done: result_url_path column added")

            # 기존 데이터에 기본 URL 경로 설정 (시작 페이지와 동일)
            print("Setting default result URL paths...")
            conn.execute(text("UPDATE fortune_service_config SET result_url_path = url_path WHERE result_url_path IS NULL"))
            conn.commit()
            print("Done: Default result URL paths set")
        else:
            print("result_url_path column already exists")

if __name__ == "__main__":
    add_result_url_path_column()
