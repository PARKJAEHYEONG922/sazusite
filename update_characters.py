"""
캐릭터 이름 및 서브배너 업데이트 스크립트
"""
import sqlite3

# DB 연결
conn = sqlite3.connect('myeongwolheon.db')
cursor = conn.cursor()

print("=" * 80)
print("캐릭터 업데이트 시작")
print("=" * 80)

# 1. 신년운세 캐릭터 변경: 야광묘 → 신월도사
print("\n[1] 신년운세 캐릭터: 야광묘 → 신월도사")
cursor.execute("""
    UPDATE fortune_service_config
    SET character_name = '신월도사',
        character_emoji = '🌕',
        subtitle = '신월도사가 펼쳐드려요',
        description = '2026년 갑오년(甲午年), 한 해 운세를 미리 살펴보세요'
    WHERE code = 'newyear2026'
""")
print("✅ 신년운세: 신월도사로 변경 완료")

# 2. 정통사주 캐릭터 변경: 청월아씨 → 청운아씨
print("\n[2] 정통사주 캐릭터: 청월아씨 → 청운아씨")
cursor.execute("""
    UPDATE fortune_service_config
    SET character_name = '청운아씨',
        character_emoji = '🕯',
        subtitle = '청운아씨가 짚어드려요',
        description = '타고난 운명의 흐름, 인생의 큰 그림을 보세요'
    WHERE code = 'saju'
""")
print("✅ 정통사주: 청운아씨로 변경 완료")

# 3. 서브배너 순서 변경 (today를 마지막으로)
print("\n[3] 서브배너 텍스트 업데이트")
updates = {
    'sub_banner_title_1': '2026 신년운세',
    'sub_banner_subtitle_1': '신월도사가 펼쳐드려요',
    'sub_banner_description_1': '2026년 갑오년(甲午年), 한 해 운세를 미리 살펴보세요',
    'sub_banner_emoji_1': '🌕',
    'sub_banner_link_1': '/fortune/newyear2026',

    'sub_banner_title_2': '정통 사주팔자',
    'sub_banner_subtitle_2': '청운아씨가 짚어드려요',
    'sub_banner_description_2': '타고난 운명의 흐름, 인생의 큰 그림을 보세요',
    'sub_banner_emoji_2': '🕯',
    'sub_banner_link_2': '/fortune/saju',

    'sub_banner_title_3': '사주궁합',
    'sub_banner_subtitle_3': '월하낭자가 맺어드려요',
    'sub_banner_description_3': '두 사람의 팔자가 만나 빚어낼 운명을 살펴보세요',
    'sub_banner_emoji_3': '💘',
    'sub_banner_link_3': '/fortune/match',

    'sub_banner_title_4': '오늘의 운세',
    'sub_banner_subtitle_4': '야광묘가 펼쳐드려요',
    'sub_banner_description_4': '오늘 하루, 당신에게 펼쳐질 운의 흐름을 봐드려요',
    'sub_banner_emoji_4': '🌙',
    'sub_banner_link_4': '/fortune/today',
}

for key, value in updates.items():
    cursor.execute(f"UPDATE site_config SET {key} = ?", (value,))

print("✅ 서브배너 순서: 신년운세 → 정통사주 → 사주궁합 → 오늘의운세")

# 커밋
conn.commit()

# 최종 확인
print("\n" + "=" * 80)
print("최종 결과 확인")
print("=" * 80)

print("\n[서비스 캐릭터]")
cursor.execute("SELECT code, title, character_name, character_emoji FROM fortune_service_config WHERE is_active = 1 ORDER BY code")
for row in cursor.fetchall():
    print(f"  {row[1]}: {row[2]} {row[3]}")

print("\n[서브배너 설정]")
cursor.execute("SELECT sub_banner_title_1, sub_banner_subtitle_1, sub_banner_title_2, sub_banner_subtitle_2, sub_banner_title_3, sub_banner_subtitle_3, sub_banner_title_4, sub_banner_subtitle_4 FROM site_config LIMIT 1")
result = cursor.fetchone()
if result:
    print(f"  1. {result[0]}: {result[1]}")
    print(f"  2. {result[2]}: {result[3]}")
    print(f"  3. {result[4]}: {result[5]}")
    print(f"  4. {result[6]}: {result[7]}")

conn.close()

print("\n" + "=" * 80)
print("캐릭터 업데이트 완료!")
print("=" * 80)
