"""
신년운세 서브배너 업데이트 (신월도사로 변경)
"""
import sqlite3

conn = sqlite3.connect('myeongwolheon.db')
cursor = conn.cursor()

print("=" * 80)
print("신년운세 서브배너 업데이트 시작")
print("=" * 80)

# 서브배너 1번 업데이트 (신년운세)
cursor.execute("""
    UPDATE site_config SET
        sub_banner_subtitle_1 = '신월도사가 비춰드려요'
    WHERE id = 1
""")

print("✅ 신년운세 서브배너 업데이트 완료")
print("   - 야광묘가 펼쳐드려요 → 신월도사가 비춰드려요")

conn.commit()

# 최종 확인
print("\n" + "=" * 80)
print("업데이트된 서브배너 1번 정보")
print("=" * 80)
cursor.execute("SELECT sub_banner_title_1, sub_banner_subtitle_1, sub_banner_emoji_1 FROM site_config LIMIT 1")
result = cursor.fetchone()
print(f"제목: {result[0]}")
print(f"부제목: {result[1]}")
print(f"이모지: {result[2]}")

conn.close()

print("\n" + "=" * 80)
print("완료!")
print("=" * 80)
