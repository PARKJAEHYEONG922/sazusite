"""
Add New Year fortune service to database
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import SessionLocal
from app.models.service_config import FortuneServiceConfig

def add_newyear_service():
    db = SessionLocal()

    try:
        # Check if newyear service already exists
        existing = db.query(FortuneServiceConfig).filter(
            FortuneServiceConfig.code == "newyear"
        ).first()

        if existing:
            print("[INFO] New Year fortune service already exists")
            return

        # Create new service entry
        newyear_service = FortuneServiceConfig(
            code="newyear",
            title="2026년 신년운세",
            subtitle="새해의 운을 미리 확인하세요",
            description="새로운 한 해의 전반적인 운세와 조언을 받아보세요",
            character_name="복신",
            character_emoji="🎊✨",
            is_active=True
        )

        db.add(newyear_service)
        db.commit()

        print("[OK] New Year fortune service added successfully!")
        print(f"    Code: {newyear_service.code}")
        print(f"    Title: {newyear_service.title}")
        print(f"    Character: {newyear_service.character_name} {newyear_service.character_emoji}")

    except Exception as e:
        print(f"[ERROR] Failed to add service: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_newyear_service()
