"""
SEO 및 스크립트 필드 추가 마이그레이션
"""
import sqlite3
from pathlib import Path

def add_seo_fields():
    """site_config 테이블에 SEO 필드 추가"""
    db_path = Path("myeongwolheon.db")

    if not db_path.exists():
        print("[ERROR] Database file not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 추가할 컬럼 리스트
    new_columns = [
        ("seo_title", "VARCHAR(200)"),
        ("seo_description", "TEXT"),
        ("seo_keywords", "TEXT"),
        ("seo_author", "VARCHAR(100)", "'명월헌'"),
        ("seo_og_image", "VARCHAR(500)"),
        ("header_script", "TEXT"),
        ("footer_script", "TEXT")
    ]

    # 기존 컬럼 확인
    cursor.execute("PRAGMA table_info(site_config)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # 컬럼 추가
    for column_info in new_columns:
        column_name = column_info[0]
        column_type = column_info[1]
        default_value = column_info[2] if len(column_info) > 2 else None

        if column_name not in existing_columns:
            try:
                if default_value:
                    sql = f"ALTER TABLE site_config ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
                else:
                    sql = f"ALTER TABLE site_config ADD COLUMN {column_name} {column_type}"

                cursor.execute(sql)
                print(f"[OK] Added column: {column_name}")
            except sqlite3.Error as e:
                print(f"[ERROR] Failed to add {column_name}: {e}")
        else:
            print(f"[INFO] Column {column_name} already exists.")

    conn.commit()
    conn.close()
    print("\n[SUCCESS] Migration completed!")

if __name__ == "__main__":
    print("Starting SEO fields migration...\n")
    add_seo_fields()
