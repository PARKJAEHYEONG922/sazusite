"""
site_url 필드 추가 마이그레이션
"""
import sqlite3
from pathlib import Path

def add_site_url_field():
    """site_config 테이블에 site_url 필드 추가"""
    db_path = Path("myeongwolheon.db")

    if not db_path.exists():
        print("[ERROR] Database file not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 기존 컬럼 확인
    cursor.execute("PRAGMA table_info(site_config)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "site_url" not in existing_columns:
        try:
            sql = "ALTER TABLE site_config ADD COLUMN site_url VARCHAR(200)"
            cursor.execute(sql)
            print("[OK] Added column: site_url")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to add site_url: {e}")
    else:
        print("[INFO] Column site_url already exists.")

    conn.commit()
    conn.close()
    print("\n[SUCCESS] Migration completed!")

if __name__ == "__main__":
    print("Starting site_url field migration...\n")
    add_site_url_field()
