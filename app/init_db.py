"""
데이터베이스 초기화 및 seed 데이터 삽입
"""
import sys
import io

# Windows 인코딩 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import engine, SessionLocal, create_tables
from app.models import SiteConfig, FortuneServiceConfig, AdminUser
from app.utils.security import get_password_hash
from app.config import get_settings

settings = get_settings()


def init_database():
    """데이터베이스 초기화"""
    print("데이터베이스 테이블 생성 중...")
    create_tables()
    print("[OK] 테이블 생성 완료!")

    db = SessionLocal()

    try:
        # 1. 사이트 설정 초기화
        print("\n사이트 설정 초기화 중...")
        site_config = db.query(SiteConfig).first()
        if not site_config:
            site_config = SiteConfig(
                site_name="명월헌",
                main_title="명월헌 – 야광묘가 알려주는 오늘의 기운",
                main_subtitle="전통 운세와 AI가 만나 더욱 정확한 운세를 알려드립니다",
                hero_image_url="/static/images/hero.jpg",
                quick_fortune_title="빠른 운세 보기",
                quick_fortune_description="간단한 정보 입력으로 바로 확인하세요",
                footer_text="© 2025 명월헌(明月軒). All rights reserved.",
                adsense_client_id=None,
                adsense_slot_main=None,
                adsense_slot_result=None
            )
            db.add(site_config)
            db.commit()
            print("[OK] 사이트 설정 생성 완료!")
        else:
            print("[SKIP] 사이트 설정이 이미 존재합니다.")

        # 2. 서비스 설정 초기화 (4개)
        print("\n서비스 설정 초기화 중...")
        services_data = [
            {
                "code": "today",
                "title": "오늘의 운세",
                "subtitle": "야광묘가 알려드려요",
                "description": "행운의 색상·숫자·방향을 확인하세요",
                "character_name": "야광묘",
                "character_emoji": "🐱✨",
                "is_active": True,
                "prompt_template": None
            },
            {
                "code": "saju",
                "title": "정통 사주팔자",
                "subtitle": "청월아씨가 풀어드려요",
                "description": "당신의 사주를 깊이 살펴봅니다",
                "character_name": "청월아씨",
                "character_emoji": "👘",
                "is_active": True,
                "prompt_template": None
            },
            {
                "code": "match",
                "title": "사주궁합",
                "subtitle": "월하낭자가 알려드려요",
                "description": "두 사람의 인연을 살펴봅니다",
                "character_name": "월하낭자",
                "character_emoji": "💕",
                "is_active": True,
                "prompt_template": None
            },
            {
                "code": "dream",
                "title": "꿈해몽",
                "subtitle": "백운선생이 해석해드려요",
                "description": "꿈이 전하는 메시지를 풀어드립니다",
                "character_name": "백운선생",
                "character_emoji": "☁️",
                "is_active": True,
                "prompt_template": None
            }
        ]

        for service_data in services_data:
            existing = db.query(FortuneServiceConfig).filter(
                FortuneServiceConfig.code == service_data["code"]
            ).first()

            if not existing:
                service = FortuneServiceConfig(**service_data)
                db.add(service)
                print(f"  [OK] {service_data['title']} ({service_data['code']}) 생성 완료!")
            else:
                print(f"  [SKIP] {service_data['title']} ({service_data['code']})이 이미 존재합니다.")

        db.commit()

        # 3. 관리자 계정 초기화
        print("\n관리자 계정 초기화 중...")
        admin = db.query(AdminUser).filter(
            AdminUser.username == settings.admin_username
        ).first()

        if not admin:
            admin = AdminUser(
                username=settings.admin_username,
                password_hash=get_password_hash(settings.admin_password)
            )
            db.add(admin)
            db.commit()
            print(f"[OK] 관리자 계정 생성 완료!")
            print(f"   ID: {settings.admin_username}")
            print(f"   PW: {settings.admin_password}")
        else:
            print("[SKIP] 관리자 계정이 이미 존재합니다.")

        print("\n" + "="*50)
        print("[SUCCESS] 데이터베이스 초기화가 완료되었습니다!")
        print("="*50)

    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
