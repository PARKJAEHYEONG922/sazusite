"""
서브배너 5번 추가 (오늘의 운세)
"""
import sqlite3

conn = sqlite3.connect('myeongwolheon.db')
cursor = conn.cursor()

print("=" * 80)
print("서브배너 5번 컬럼 추가 시작")
print("=" * 80)

# 5번 서브배너 컬럼들 추가
columns_to_add = [
    ('sub_banner_title_5', 'TEXT'),
    ('sub_banner_subtitle_5', 'TEXT'),
    ('sub_banner_description_5', 'TEXT'),
    ('sub_banner_emoji_5', 'TEXT'),
    ('sub_banner_link_5', 'TEXT'),
    ('sub_banner_image_5', 'TEXT'),
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f'ALTER TABLE site_config ADD COLUMN {col_name} {col_type}')
        print(f"✅ {col_name} 컬럼 추가 완료")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print(f"⚠️  {col_name} 컬럼 이미 존재")
        else:
            raise

# 5번 서브배너 데이터 입력
print("\n서브배너 5번 데이터 입력...")
cursor.execute('''
    UPDATE site_config SET
    sub_banner_title_5 = '오늘의 운세',
    sub_banner_subtitle_5 = '야광묘가 펼쳐드려요',
    sub_banner_description_5 = '오늘 하루, 당신에게 펼쳐질 운의 흐름을 봐드려요',
    sub_banner_emoji_5 = '🌙',
    sub_banner_link_5 = '/fortune/today',
    sub_banner_image_5 = NULL
''')

conn.commit()

# 최종 확인
print("\n" + "=" * 80)
print("최종 서브배너 목록 (5개)")
print("=" * 80)
cursor.execute('''
    SELECT
        sub_banner_title_1, sub_banner_subtitle_1,
        sub_banner_title_2, sub_banner_subtitle_2,
        sub_banner_title_3, sub_banner_subtitle_3,
        sub_banner_title_4, sub_banner_subtitle_4,
        sub_banner_title_5, sub_banner_subtitle_5
    FROM site_config LIMIT 1
''')
result = cursor.fetchone()

for i in range(5):
    title_idx = i * 2
    subtitle_idx = i * 2 + 1
    print(f"{i+1}. {result[title_idx]}: {result[subtitle_idx]}")

conn.close()

print("\n" + "=" * 80)
print("서브배너 5번 추가 완료!")
print("=" * 80)
