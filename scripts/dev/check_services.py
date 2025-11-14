"""
Check all services in database
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import SessionLocal
from app.models.service_config import FortuneServiceConfig

def check_services():
    db = SessionLocal()
    try:
        services = db.query(FortuneServiceConfig).all()
        print("\n=== 현재 등록된 서비스 ===")
        for s in services:
            print(f"{s.code}: {s.title} - {s.character_name} {s.character_emoji}")
    finally:
        db.close()

if __name__ == "__main__":
    check_services()
