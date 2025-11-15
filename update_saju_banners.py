"""
정통사주 배너 텍스트 업데이트 (청월아씨 → 청운아씨)
"""
import sqlite3

conn = sqlite3.connect('myeongwolheon.db')
cursor = conn.cursor()

print("=" * 80)
print("정통사주 배너 텍스트 업데이트 시작")
print("=" * 80)

# 서브배너 2번 및 메인배너 2번 업데이트
cursor.execute("""
    UPDATE site_config SET
        sub_banner_subtitle_2 = '청운아씨가 짚어드려요',
        banner_subtitle_2 = '청운아씨가 풀어드려요'
    WHERE id = 1
""")

print("✅ 배너 텍스트 업데이트 완료")
print("   - 서브배너 2: 청월아씨가 짚어드려요 → 청운아씨가 짚어드려요")
print("   - 메인배너 2: 청월아씨가 풀어드려요 → 청운아씨가 풀어드려요")

conn.commit()

# 최종 확인
print("\n" + "=" * 80)
print("업데이트된 배너 정보")
print("=" * 80)
cursor.execute("SELECT sub_banner_title_2, sub_banner_subtitle_2, banner_title_2, banner_subtitle_2 FROM site_config LIMIT 1")
result = cursor.fetchone()
print(f"서브배너 2: {result[0]} - {result[1]}")
print(f"메인배너 2: {result[2]} - {result[3]}")

conn.close()

print("\n" + "=" * 80)
print("완료!")
print("=" * 80)
