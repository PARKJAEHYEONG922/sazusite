"""
사이트 전체 설정 모델
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SiteConfig(Base):
    """사이트 전체 설정"""
    __tablename__ = "site_config"

    id = Column(Integer, primary_key=True, index=True)

    # 기본 정보
    site_name = Column(String(100), default="명월헌")
    site_url = Column(String(200), nullable=True)  # 사이트 URL (예: https://yourdomain.com)
    site_logo = Column(String(500), nullable=True)  # 사이트 로고 이미지
    site_favicon = Column(String(500), nullable=True)  # 사이트 파비콘 (.ico, .png)
    main_title = Column(String(200), default="명월헌 – 야광묘가 알려주는 오늘의 기운")
    main_subtitle = Column(Text, default="전통 운세와 AI가 만나 더욱 정확한 운세를 알려드립니다")

    # 메인 배너 설정 (모바일: 4:3, PC: 21:9)
    # 배너 1
    banner_image_1 = Column(String(500), nullable=True)  # 모바일용 (4:3)
    banner_image_pc_1 = Column(String(500), nullable=True)  # PC용 (21:9)
    banner_title_1 = Column(String(100), default="오늘의 운세")
    banner_subtitle_1 = Column(String(200), default="야광묘가 알려드려요")
    banner_description_1 = Column(Text, default="매일 새로운 운세로 하루를 시작하세요")
    banner_link_1 = Column(String(500), default="/fortune/today")

    # 배너 2
    banner_image_2 = Column(String(500), nullable=True)  # 모바일용 (4:3)
    banner_image_pc_2 = Column(String(500), nullable=True)  # PC용 (21:9)
    banner_title_2 = Column(String(100), default="정통 사주팔자")
    banner_subtitle_2 = Column(String(200), default="청월아씨가 풀어드려요")
    banner_description_2 = Column(Text, default="태어난 시간으로 알아보는 나의 운명")
    banner_link_2 = Column(String(500), default="/fortune/saju")

    # 배너 3
    banner_image_3 = Column(String(500), nullable=True)  # 모바일용 (4:3)
    banner_image_pc_3 = Column(String(500), nullable=True)  # PC용 (21:9)
    banner_title_3 = Column(String(100), default="사주궁합")
    banner_subtitle_3 = Column(String(200), default="월하낭자가 알려드려요")
    banner_description_3 = Column(Text, default="두 사람의 인연과 미래를 함께 살펴보세요")
    banner_link_3 = Column(String(500), default="/fortune/match")

    # 배너 4
    banner_image_4 = Column(String(500), nullable=True)  # 모바일용 (4:3)
    banner_image_pc_4 = Column(String(500), nullable=True)  # PC용 (21:9)
    banner_title_4 = Column(String(100), default="꿈해몽")
    banner_subtitle_4 = Column(String(200), default="백운선생이 해석해드려요")
    banner_description_4 = Column(Text, default="당신의 꿈이 전하는 메시지를 찾아보세요")
    banner_link_4 = Column(String(500), default="/fortune/dream")

    # 서브 배너 (서비스 카드) - 3:4 비율
    # 서브배너 1
    sub_banner_image_1 = Column(String(500), nullable=True)
    sub_banner_emoji_1 = Column(String(10), default="🌙")
    sub_banner_title_1 = Column(String(100), default="월하소녀 2026 신년운세")
    sub_banner_subtitle_1 = Column(String(200), default="월하소녀 2026 신년운세")
    sub_banner_description_1 = Column(Text, default="이번 신년, 당신의 운명은?")
    sub_banner_link_1 = Column(String(500), default="/fortune/newyear2026")

    # 서브배너 2
    sub_banner_image_2 = Column(String(500), nullable=True)
    sub_banner_emoji_2 = Column(String(10), default="📜")
    sub_banner_title_2 = Column(String(100), default="청월아씨 정통사주")
    sub_banner_subtitle_2 = Column(String(200), default="청월아씨 정통사주")
    sub_banner_description_2 = Column(Text, default="내 앞에 펼쳐진 운명의 길은?")
    sub_banner_link_2 = Column(String(500), default="/fortune/saju")

    # 서브배너 3
    sub_banner_image_3 = Column(String(500), nullable=True)
    sub_banner_emoji_3 = Column(String(10), default="💘")
    sub_banner_title_3 = Column(String(100), default="홍연아씨 사주궁합")
    sub_banner_subtitle_3 = Column(String(200), default="홍연아씨 사주궁합")
    sub_banner_description_3 = Column(Text, default="우리는 운명일까, 우연일까?")
    sub_banner_link_3 = Column(String(500), default="/fortune/match")

    # 서브배너 4
    sub_banner_image_4 = Column(String(500), nullable=True)
    sub_banner_emoji_4 = Column(String(10), default="💭")
    sub_banner_title_4 = Column(String(100), default="몽월소녀 꿈해몽")
    sub_banner_subtitle_4 = Column(String(200), default="몽월소녀 꿈해몽")
    sub_banner_description_4 = Column(Text, default="어젯 밤 꿈, 무슨 의미일까?")
    sub_banner_link_4 = Column(String(500), default="/fortune/dream")

    # 서브배너 5
    sub_banner_image_5 = Column(String(500), nullable=True)
    sub_banner_emoji_5 = Column(String(10), default="🌙")
    sub_banner_title_5 = Column(String(100), default="오늘의 운세")
    sub_banner_subtitle_5 = Column(String(200), default="야광묘가 펼쳐드려요")
    sub_banner_description_5 = Column(Text, default="오늘 하루, 당신에게 펼쳐질 운의 흐름을 봐드려요")
    sub_banner_link_5 = Column(String(500), default="/fortune/today")

    # 빠른 운세
    quick_fortune_title = Column(String(100), default="빠른 운세 보기")
    quick_fortune_description = Column(Text, default="간단한 정보 입력으로 바로 확인하세요")

    # 푸터
    footer_text = Column(Text, default="© 2025 명월헌(明月軒). All rights reserved.")

    # 애드센스
    adsense_client_id = Column(String(100), nullable=True)
    adsense_slot_main = Column(String(100), nullable=True)
    adsense_slot_result = Column(String(100), nullable=True)

    # SNS 공유
    kakao_javascript_key = Column(String(100), nullable=True)  # 카카오 JavaScript 키 (공유 기능용)

    # SEO 메타태그
    seo_title = Column(String(200), nullable=True)  # 기본 SEO 타이틀
    seo_description = Column(Text, nullable=True)  # 기본 SEO 설명
    seo_keywords = Column(Text, nullable=True)  # 기본 SEO 키워드
    seo_author = Column(String(100), default="명월헌")
    seo_og_image = Column(String(500), nullable=True)  # 기본 OG 이미지

    # 헤더/푸터 스크립트
    header_script = Column(Text, nullable=True)  # <head> 안에 삽입할 스크립트 (Google Analytics, 메타태그 등)
    footer_script = Column(Text, nullable=True)  # </body> 전에 삽입할 스크립트 (채팅, 트래킹 등)

    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
