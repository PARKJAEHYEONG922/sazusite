"""
카카오 JavaScript 키 DB에 업데이트
"""
import sqlite3

def update_kakao_key():
    """카카오 JavaScript 키 업데이트"""
    conn = sqlite3.connect('myeongwolheon.db')
    cursor = conn.cursor()

    try:
        # 카카오 키 업데이트
        cursor.execute("""
            UPDATE site_config
            SET kakao_javascript_key = ?
            WHERE id = 1
        """, ('5f32b894a9d03985f7f6bc51e969e445',))

        conn.commit()
        print("[OK] 카카오 JavaScript 키가 업데이트되었습니다!")

        # 확인
        cursor.execute("SELECT kakao_javascript_key FROM site_config WHERE id = 1")
        result = cursor.fetchone()
        if result:
            print(f"[확인] 저장된 키: {result[0]}")

    except Exception as e:
        print(f"[ERROR] 업데이트 실패: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_kakao_key()
