"""
FortuneResult 테이블에 status와 error_message 컬럼 추가
"""
import sys
import io

# Windows 인코딩 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlalchemy import text
from app.database import engine

def add_status_columns():
    """status와 error_message 컬럼 추가"""
    print("FortuneResult 테이블에 status와 error_message 컬럼 추가 중...")

    with engine.connect() as conn:
        try:
            # status 컬럼 추가
            conn.execute(text("""
                ALTER TABLE fortune_result
                ADD COLUMN status VARCHAR(20) DEFAULT 'completed'
            """))
            print("[OK] status 컬럼 추가 완료!")

            # error_message 컬럼 추가
            conn.execute(text("""
                ALTER TABLE fortune_result
                ADD COLUMN error_message TEXT
            """))
            print("[OK] error_message 컬럼 추가 완료!")

            # 기존 데이터의 status를 'completed'로 설정 (result_text가 있는 경우)
            conn.execute(text("""
                UPDATE fortune_result
                SET status = 'completed'
                WHERE result_text IS NOT NULL
            """))
            print("[OK] 기존 데이터 상태 업데이트 완료!")

            conn.commit()
            print("\n" + "="*50)
            print("[SUCCESS] 마이그레이션이 완료되었습니다!")
            print("="*50)

        except Exception as e:
            print(f"\n[ERROR] 오류 발생: {e}")
            # 컬럼이 이미 존재하면 무시
            if "already exists" in str(e) or "duplicate column name" in str(e).lower():
                print("[INFO] 컬럼이 이미 존재합니다. 스킵합니다.")
            else:
                conn.rollback()
                raise

if __name__ == "__main__":
    add_status_columns()
