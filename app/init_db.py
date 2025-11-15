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
                banner_image_1=None,
                banner_title_1="오늘의 운세",
                banner_subtitle_1="야광묘가 알려드려요",
                banner_description_1="매일 새로운 운세로 하루를 시작하세요",
                banner_link_1="/fortune/today",
                banner_image_2=None,
                banner_title_2="정통 사주팔자",
                banner_subtitle_2="청월아씨가 풀어드려요",
                banner_description_2="태어난 시간으로 알아보는 나의 운명",
                banner_link_2="/fortune/saju",
                banner_image_3=None,
                banner_title_3="사주궁합",
                banner_subtitle_3="월하낭자가 알려드려요",
                banner_description_3="두 사람의 인연과 미래를 함께 살펴보세요",
                banner_link_3="/fortune/match",
                banner_image_4=None,
                banner_title_4="꿈해몽",
                banner_subtitle_4="백운선생이 해석해드려요",
                banner_description_4="당신의 꿈이 전하는 메시지를 찾아보세요",
                banner_link_4="/fortune/dream",
                # 서브배너
                sub_banner_image_1=None,
                sub_banner_emoji_1="🐱✨",
                sub_banner_title_1="신년운세",
                sub_banner_subtitle_1="야광묘가 알려드려요",
                sub_banner_description_1="2026년 새해 운세를 미리 확인하세요",
                sub_banner_link_1="/fortune/newyear2026",
                sub_banner_image_2=None,
                sub_banner_emoji_2="👘",
                sub_banner_title_2="정통사주",
                sub_banner_subtitle_2="청월아씨가 알려드려요",
                sub_banner_description_2="내 앞에 펼쳐진 운명의 길은?",
                sub_banner_link_2="/fortune/saju",
                sub_banner_image_3=None,
                sub_banner_emoji_3="💕",
                sub_banner_title_3="사주궁합",
                sub_banner_subtitle_3="월하낭자가 알려드려요",
                sub_banner_description_3="우리는 운명일까, 우연일까?",
                sub_banner_link_3="/fortune/match",
                sub_banner_image_4=None,
                sub_banner_emoji_4="☁️",
                sub_banner_title_4="꿈해몽",
                sub_banner_subtitle_4="백운선생이 알려드려요",
                sub_banner_description_4="어젯 밤 꿈, 무슨 의미일까?",
                sub_banner_link_4="/fortune/dream",
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

        # 2. 서비스 설정 초기화 (5개)
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
                "prompt_template": None,
                "loading_title": "오늘의 운세를 계산하고 있습니다",
                "loading_subtitle": "야광묘가 당신의 사주를 깊이 살펴보고 있어요",
                "loading_detail": "AI가 생년월일 기반 천간지지 데이터로 오늘의 기운을 분석 중..."
            },
            {
                "code": "saju",
                "title": "정통 사주팔자",
                "subtitle": "청월아씨가 풀어드려요",
                "description": "당신의 사주를 깊이 살펴봅니다",
                "character_name": "청월아씨",
                "character_emoji": "👘",
                "is_active": True,
                "prompt_template": None,
                "loading_title": "당신의 사주명식을 분석하고 있습니다",
                "loading_subtitle": "청월아씨가 운명의 흐름을 읽어내고 있어요",
                "loading_detail": "AI가 계산된 사주팔자를 깊이 분석 중..."
            },
            {
                "code": "match",
                "title": "사주궁합",
                "subtitle": "월하낭자가 알려드려요",
                "description": "두 사람의 인연을 살펴봅니다",
                "character_name": "월하낭자",
                "character_emoji": "💕",
                "is_active": True,
                "prompt_template": None,
                "loading_title": "두 분의 궁합을 분석하고 있습니다",
                "loading_subtitle": "월하낭자가 두 사주의 만남을 살펴보고 있어요",
                "loading_detail": "AI가 천간지지 기반 데이터로 천생연분을 찾는 중..."
            },
            {
                "code": "dream",
                "title": "꿈해몽",
                "subtitle": "백운선생이 해석해드려요",
                "description": "꿈이 전하는 메시지를 풀어드립니다",
                "character_name": "백운선생",
                "character_emoji": "☁️",
                "is_active": True,
                "prompt_template": None,
                "loading_title": "백운선생께서 꿈을 풀이하고 계십니다",
                "loading_subtitle": "꿈 속 상징과 의미를 해석하고 있어요",
                "loading_detail": "AI가 오랜 해몽 지식 기반으로 꿈의 길흉화복을 살피는 중..."
            },
            {
                "code": "newyear2026",
                "title": "2026 신년운세",
                "subtitle": "야광묘가 알려드려요",
                "description": "2026년 새해, 당신의 운명을 미리 살펴보세요",
                "character_name": "야광묘",
                "character_emoji": "🐱✨",
                "is_active": True,
                "prompt_template": None,
                "loading_title": "2026년 신년운세를 계산하고 있습니다",
                "loading_subtitle": "야광묘가 병오년의 기운을 살펴보고 있어요",
                "loading_detail": "AI가 천간지지 기반 데이터로 새해 운세를 풀어내는 중..."
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
