"""
데이터베이스의 이미지 URL을 .webp로 수정
"""
import sqlite3
from pathlib import Path
import sys
import io

# Windows 인코딩 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fix_webp_urls():
    """데이터베이스의 이미지 URL을 .webp로 업데이트"""
    db_path = Path("myeongwolheon.db")

    if not db_path.exists():
        print("[ERROR] 데이터베이스 파일이 없습니다.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("\n=== 데이터베이스 URL 업데이트 시작 ===\n")

        # site_config 테이블 업데이트
        updates = [
            # 로고
            ("site_logo", "site_logo.png", "site_logo.webp"),

            # 배너 (모바일)
            ("banner_image_1", "banner_1.png", "banner_1.webp"),
            ("banner_image_2", "banner_2.png", "banner_2.webp"),
            ("banner_image_3", "banner_3.png", "banner_3.webp"),
            ("banner_image_4", "banner_4.png", "banner_4.webp"),

            # 배너 (PC)
            ("banner_image_pc_1", "banner_pc_1.png", "banner_pc_1.webp"),
            ("banner_image_pc_2", "banner_pc_2.png", "banner_pc_2.webp"),
            ("banner_image_pc_3", "banner_pc_3.png", "banner_pc_3.webp"),
            ("banner_image_pc_4", "banner_pc_4.png", "banner_pc_4.webp"),

            # 서브배너
            ("sub_banner_image_1", "sub_banner_1.png", "sub_banner_1.webp"),
            ("sub_banner_image_2", "sub_banner_2.png", "sub_banner_2.webp"),
            ("sub_banner_image_3", "sub_banner_3.png", "sub_banner_3.webp"),
            ("sub_banner_image_4", "sub_banner_4.png", "sub_banner_4.webp"),
        ]

        for column, old_file, new_file in updates:
            cursor.execute(f"""
                UPDATE site_config
                SET {column} = REPLACE({column}, '{old_file}', '{new_file}')
                WHERE {column} LIKE '%{old_file}%'
            """)

            if cursor.rowcount > 0:
                print(f"[OK] {column}: {old_file} → {new_file}")

        conn.commit()
        print("\n[SUCCESS] 데이터베이스 URL 업데이트 완료!")

        # 업데이트된 데이터 확인
        print("\n=== 업데이트 결과 확인 ===\n")
        cursor.execute("SELECT site_logo, banner_image_1, banner_image_2, sub_banner_image_1 FROM site_config LIMIT 1")
        result = cursor.fetchone()

        if result:
            print(f"site_logo: {result[0]}")
            print(f"banner_image_1: {result[1]}")
            print(f"banner_image_2: {result[2]}")
            print(f"sub_banner_image_1: {result[3]}")

    except Exception as e:
        print(f"[ERROR] 업데이트 실패: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_webp_urls()
