"""
데이터베이스 연결 테스트 스크립트
SQLite와 PostgreSQL 연결을 테스트합니다.
"""
from sqlalchemy import create_engine, text
from app.config import Settings

def test_database_connection():
    """데이터베이스 연결 테스트"""
    settings = Settings()

    print("=" * 60)
    print("데이터베이스 연결 테스트")
    print("=" * 60)
    print(f"\nDATABASE_URL: {settings.database_url}")
    print(f"ENVIRONMENT: {settings.environment}")
    print(f"DEBUG: {settings.debug}\n")

    try:
        # 엔진 생성
        engine = create_engine(settings.database_url)

        # 연결 테스트
        with engine.connect() as conn:
            # 데이터베이스 버전 확인
            if "sqlite" in settings.database_url:
                result = conn.execute(text("SELECT sqlite_version()"))
                version = result.fetchone()[0]
                print(f"[OK] SQLite 연결 성공!")
                print(f"     버전: {version}")
            elif "postgresql" in settings.database_url:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"[OK] PostgreSQL 연결 성공!")
                print(f"     버전: {version[:50]}...")

            # 테이블 목록 확인
            if "sqlite" in settings.database_url:
                result = conn.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ))
            else:
                result = conn.execute(text(
                    "SELECT tablename FROM pg_tables WHERE schemaname='public'"
                ))

            tables = [row[0] for row in result.fetchall()]
            print(f"\n기존 테이블: {len(tables)}개")
            for table in tables:
                print(f"   - {table}")

        print("\n" + "=" * 60)
        print("[OK] 모든 테스트 통과!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERROR] 연결 실패: {str(e)}")
        print("\nPostgreSQL 사용 시 확인사항:")
        print("   1. PostgreSQL 서버가 실행 중인지 확인")
        print("   2. 데이터베이스가 생성되었는지 확인")
        print("   3. 사용자 권한이 올바른지 확인")
        print("   4. .env 파일의 DATABASE_URL이 정확한지 확인")
        print("\n" + "=" * 60)
        return False

if __name__ == "__main__":
    test_database_connection()
