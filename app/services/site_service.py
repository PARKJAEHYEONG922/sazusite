"""
사이트 설정 서비스
"""
from sqlalchemy.orm import Session
from app.models.site_config import SiteConfig
from app.models.service_config import FortuneServiceConfig
from typing import List, Optional


class SiteService:
    """사이트 및 서비스 설정 관리"""

    def __init__(self, db: Session):
        self.db = db

    def get_site_config(self) -> Optional[SiteConfig]:
        """사이트 설정 조회"""
        return self.db.query(SiteConfig).first()

    def update_site_config(self, updates: dict) -> SiteConfig:
        """사이트 설정 업데이트"""
        config = self.get_site_config()

        if not config:
            # 없으면 생성
            config = SiteConfig(**updates)
            self.db.add(config)
        else:
            # 업데이트
            for key, value in updates.items():
                if value is not None and hasattr(config, key):
                    setattr(config, key, value)

        self.db.commit()
        self.db.refresh(config)
        return config

    def get_all_services(self) -> List[FortuneServiceConfig]:
        """모든 서비스 설정 조회"""
        return self.db.query(FortuneServiceConfig).all()

    def get_active_services(self) -> List[FortuneServiceConfig]:
        """활성화된 서비스만 조회"""
        return self.db.query(FortuneServiceConfig).filter(
            FortuneServiceConfig.is_active == True
        ).all()

    def get_service_by_code(self, code: str) -> Optional[FortuneServiceConfig]:
        """코드로 서비스 조회"""
        return self.db.query(FortuneServiceConfig).filter(
            FortuneServiceConfig.code == code
        ).first()

    def update_service_config(self, code: str, updates: dict) -> FortuneServiceConfig:
        """서비스 설정 업데이트"""
        service = self.get_service_by_code(code)

        if not service:
            raise ValueError(f"서비스를 찾을 수 없습니다: {code}")

        for key, value in updates.items():
            if value is not None and hasattr(service, key):
                setattr(service, key, value)

        self.db.commit()
        self.db.refresh(service)
        return service

    def create_service(self, service_data: dict) -> FortuneServiceConfig:
        """새로운 페이지(서비스) 생성"""
        # 코드 중복 확인
        existing = self.get_service_by_code(service_data.get('code'))
        if existing:
            raise ValueError(f"이미 존재하는 코드입니다: {service_data.get('code')}")

        # 새 서비스 생성
        service = FortuneServiceConfig(**service_data)
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service

    def delete_service(self, code: str) -> bool:
        """페이지(서비스) 삭제"""
        service = self.get_service_by_code(code)
        if not service:
            raise ValueError(f"서비스를 찾을 수 없습니다: {code}")

        self.db.delete(service)
        self.db.commit()
        return True
