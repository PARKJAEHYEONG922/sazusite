"""
Update site_config: 빠른 운세 제목 및 서브배너 1 링크 업데이트
"""
import sqlite3
import sys
import io

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Connect to database
conn = sqlite3.connect('myeongwolheon.db')
cursor = conn.cursor()

try:
    # 빠른 운세 제목 업데이트
    cursor.execute("""
        UPDATE site_config
        SET quick_fortune_title = '빠른 운세 보기'
    """)

    conn.commit()

    # 변경 확인
    cursor.execute("SELECT quick_fortune_title FROM site_config")
    result = cursor.fetchone()

    if result:
        print(f"✓ 업데이트 완료!")
        print(f"  - 빠른 운세 제목: {result[0]}")
    else:
        print("⚠ site_config 레코드가 없습니다. 새로 생성됩니다.")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n업데이트 완료!")
