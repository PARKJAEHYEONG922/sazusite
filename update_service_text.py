"""
서비스 설정 텍스트 업데이트 스크립트
"""
import sqlite3

# DB 연결
conn = sqlite3.connect('myeongwolheon.db')
cursor = conn.cursor()

# 각 서비스별 업데이트할 텍스트
updates = [
    {
        'code': 'today',
        'subtitle': '야광묘가 오늘의 기운을 읽어드립니다',
        'description': '하루의 시작, 오늘 당신에게 필요한 조언을 확인하세요'
    },
    {
        'code': 'newyear2026',
        'subtitle': '월하소녀가 새해의 별자리를 읽어드립니다',
        'description': '2026년 갑오년(甲午年), 한 해 운세를 미리 살펴보세요'
    },
    {
        'code': 'saju',
        'subtitle': '청월아씨가 사주 한자 한자 짚어드립니다',
        'description': '타고난 운명의 흐름, 인생의 큰 그림을 살펴보세요'
    },
    {
        'code': 'match',
        'subtitle': '월하낭자가 붉은 실을 찾아드립니다',
        'description': '두 사람의 팔자가 만나 빚어낼 운명을 살펴보세요'
    },
    {
        'code': 'dream',
        'subtitle': '백운선생이 꿈속 메시지를 풀어드립니다',
        'description': '꿈은 또 다른 세계의 암호, 그 의미를 찾아보세요'
    }
]

print("=" * 60)
print("서비스 설정 텍스트 업데이트 시작")
print("=" * 60)

for update in updates:
    code = update['code']
    subtitle = update['subtitle']
    description = update['description']

    # 기존 데이터 확인
    cursor.execute("SELECT title, subtitle, description FROM fortune_service_config WHERE code = ?", (code,))
    result = cursor.fetchone()

    if result:
        print(f"\n[{code}] 업데이트 전:")
        print(f"  Title: {result[0]}")
        print(f"  Subtitle: {result[1]}")
        print(f"  Description: {result[2]}")

        # 업데이트
        cursor.execute(
            "UPDATE fortune_service_config SET subtitle = ?, description = ? WHERE code = ?",
            (subtitle, description, code)
        )

        print(f"\n[{code}] 업데이트 후:")
        print(f"  Subtitle: {subtitle}")
        print(f"  Description: {description}")
    else:
        print(f"\n[{code}] 서비스를 찾을 수 없습니다. 건너뜁니다.")

# 변경사항 저장
conn.commit()

print("\n" + "=" * 60)
print("업데이트 완료!")
print("=" * 60)

# 최종 결과 확인
print("\n최종 서비스 설정:")
cursor.execute("SELECT code, title, subtitle, description FROM fortune_service_config WHERE is_active = 1")
for row in cursor.fetchall():
    print(f"\n[{row[0]}] {row[1]}")
    print(f"  Subtitle: {row[2]}")
    print(f"  Description: {row[3]}")

conn.close()
