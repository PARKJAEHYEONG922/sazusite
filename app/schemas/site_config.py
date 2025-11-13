"""
사이트 설정 스키마
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SiteConfigSchema(BaseModel):
    """사이트 설정 조회"""
    id: int
    site_name: str
    main_title: str
    main_subtitle: str
    hero_image_url: Optional[str]
    quick_fortune_title: str
    quick_fortune_description: str
    footer_text: str
    adsense_client_id: Optional[str]
    adsense_slot_main: Optional[str]
    adsense_slot_result: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SiteConfigUpdate(BaseModel):
    """사이트 설정 수정"""
    site_name: Optional[str] = None
    main_title: Optional[str] = None
    main_subtitle: Optional[str] = None
    hero_image_url: Optional[str] = None
    quick_fortune_title: Optional[str] = None
    quick_fortune_description: Optional[str] = None
    footer_text: Optional[str] = None
    adsense_client_id: Optional[str] = None
    adsense_slot_main: Optional[str] = None
    adsense_slot_result: Optional[str] = None
