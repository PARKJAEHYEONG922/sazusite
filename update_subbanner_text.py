"""
서브배너 텍스트 업데이트 스크립트
"""
import sqlite3

# DB 연결
conn = sqlite3.connect('myeongwolheon.db')
cursor = conn.cursor()

# 서브배너 업데이트할 텍스트
updates = {
    'sub_banner_subtitle_1': '야광묘가 펼쳐드려요',
    'sub_banner_subtitle_2': '청월아씨가 짚어드려요',
    'sub_banner_subtitle_3': '월하낭자가 맺어드려요',
    'sub_banner_subtitle_4': '백운선생이 풀어드려요',
    'sub_banner_description_1': '2026년 갑오년(甲午年), 한 해 운세를 미리 살펴보세요',
    'sub_banner_description_2': '타고난 운명의 흐름, 인생의 큰 그림을 보세요',
    'sub_banner_description_3': '두 사람의 팔자가 만나 빚어낼 운명을 살펴보세요',
    'sub_banner_description_4': '꿈은 또 다른 세계의 암호, 그 의미를 찾아보세요'
}

print("=" * 60)
print("서브배너 텍스트 업데이트 시작")
print("=" * 60)

# 기존 데이터 확인
cursor.execute("""
    SELECT sub_banner_subtitle_1, sub_banner_subtitle_2,
           sub_banner_subtitle_3, sub_banner_subtitle_4,
           sub_banner_description_1, sub_banner_description_2,
           sub_banner_description_3, sub_banner_description_4
    FROM site_config LIMIT 1
""")
result = cursor.fetchone()

if result:
    print("\n업데이트 전:")
    print(f"  서브배너1 subtitle: {result[0] if result[0] else '(없음)'}")
    print(f"  서브배너2 subtitle: {result[1] if result[1] else '(없음)'}")
    print(f"  서브배너3 subtitle: {result[2] if result[2] else '(없음)'}")
    print(f"  서브배너4 subtitle: {result[3] if result[3] else '(없음)'}")
    print(f"  서브배너1 description: {result[4] if result[4] else '(없음)'}")
    print(f"  서브배너2 description: {result[5] if result[5] else '(없음)'}")
    print(f"  서브배너3 description: {result[6] if result[6] else '(없음)'}")
    print(f"  서브배너4 description: {result[7] if result[7] else '(없음)'}")

# 업데이트
cursor.execute("""
    UPDATE site_config SET
        sub_banner_subtitle_1 = ?,
        sub_banner_subtitle_2 = ?,
        sub_banner_subtitle_3 = ?,
        sub_banner_subtitle_4 = ?,
        sub_banner_description_1 = ?,
        sub_banner_description_2 = ?,
        sub_banner_description_3 = ?,
        sub_banner_description_4 = ?
""", (
    updates['sub_banner_subtitle_1'],
    updates['sub_banner_subtitle_2'],
    updates['sub_banner_subtitle_3'],
    updates['sub_banner_subtitle_4'],
    updates['sub_banner_description_1'],
    updates['sub_banner_description_2'],
    updates['sub_banner_description_3'],
    updates['sub_banner_description_4']
))

conn.commit()

print("\n업데이트 후:")
print(f"  서브배너1 subtitle: {updates['sub_banner_subtitle_1']}")
print(f"  서브배너2 subtitle: {updates['sub_banner_subtitle_2']}")
print(f"  서브배너3 subtitle: {updates['sub_banner_subtitle_3']}")
print(f"  서브배너4 subtitle: {updates['sub_banner_subtitle_4']}")
print(f"  서브배너1 description: {updates['sub_banner_description_1']}")
print(f"  서브배너2 description: {updates['sub_banner_description_2']}")
print(f"  서브배너3 description: {updates['sub_banner_description_3']}")
print(f"  서브배너4 description: {updates['sub_banner_description_4']}")

print("\n" + "=" * 60)
print("업데이트 완료!")
print("=" * 60)

conn.close()
