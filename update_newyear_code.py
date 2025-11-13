"""
Update newyear service code to newyear2026
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import SessionLocal
from app.models.service_config import FortuneServiceConfig

def update_code():
    db = SessionLocal()
    try:
        service = db.query(FortuneServiceConfig).filter(
            FortuneServiceConfig.code == 'newyear'
        ).first()

        if service:
            print(f'기존 코드: {service.code}')
            service.code = 'newyear2026'
            db.commit()
            print(f'새 코드: {service.code}')
            print('✅ 신년운세 코드가 newyear2026으로 변경되었습니다.')
        else:
            print('❌ newyear 서비스를 찾을 수 없습니다.')
    finally:
        db.close()

if __name__ == "__main__":
    update_code()
