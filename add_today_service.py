"""
오늘의 운세 서비스 설정 추가
"""
import sqlite3

conn = sqlite3.connect('myeongwolheon.db')
cursor = conn.cursor()

print("=" * 80)
print("오늘의 운세 서비스 설정 추가 시작")
print("=" * 80)

# 기존 'today' 서비스가 있는지 확인
cursor.execute("SELECT code FROM fortune_service_config WHERE code = 'today'")
existing = cursor.fetchone()

if existing:
    print("⚠️  'today' 서비스가 이미 존재합니다. 업데이트합니다...")
    cursor.execute("""
        UPDATE fortune_service_config SET
            title = '오늘의 운세',
            description = '오늘 하루, 당신에게 펼쳐질 운의 흐름을 봐드려요',
            character_name = '야광묘',
            character_emoji = '🌙',
            subtitle = '야광묘가 펼쳐드려요',
            prompt_template = 'today.txt'
        WHERE code = 'today'
    """)
    print("✅ 'today' 서비스 업데이트 완료")
else:
    print("'today' 서비스 추가 중...")
    cursor.execute("""
        INSERT INTO fortune_service_config (
            code, title, description, character_name, character_emoji,
            subtitle, prompt_template, is_active
        ) VALUES (
            'today',
            '오늘의 운세',
            '오늘 하루, 당신에게 펼쳐질 운의 흐름을 봐드려요',
            '야광묘',
            '🌙',
            '야광묘가 펼쳐드려요',
            'today.txt',
            1
        )
    """)
    print("✅ 'today' 서비스 추가 완료")

conn.commit()

# 최종 확인
print("\n" + "=" * 80)
print("전체 서비스 목록")
print("=" * 80)
cursor.execute("SELECT code, title, character_name FROM fortune_service_config WHERE is_active = 1 ORDER BY code")
for row in cursor.fetchall():
    print(f"- {row[0]}: {row[1]} ({row[2]})")

conn.close()

print("\n" + "=" * 80)
print("오늘의 운세 서비스 설정 완료!")
print("=" * 80)
