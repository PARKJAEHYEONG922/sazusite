"""
Check dream service prompt template
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import SessionLocal
from app.models.service_config import FortuneServiceConfig

def check_prompt():
    db = SessionLocal()
    try:
        dream = db.query(FortuneServiceConfig).filter(
            FortuneServiceConfig.code == 'dream'
        ).first()

        if dream:
            print('=== 꿈해몽 프롬프트 ===')
            if dream.prompt_template:
                print(dream.prompt_template)
                print(f'\n프롬프트 길이: {len(dream.prompt_template)} 글자')
            else:
                print('프롬프트 없음 (기본 프롬프트 사용)')
        else:
            print('꿈해몽 서비스를 찾을 수 없습니다')
    finally:
        db.close()

if __name__ == "__main__":
    check_prompt()
