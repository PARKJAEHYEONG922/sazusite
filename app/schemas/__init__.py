"""
Pydantic 스키마 모듈
"""
from app.schemas.fortune import (
    FortuneRequest,
    FortuneResponse,
    TodayFortuneRequest,
    SajuFortuneRequest,
    MatchFortuneRequest,
    DreamFortuneRequest
)
from app.schemas.site_config import SiteConfigSchema, SiteConfigUpdate
from app.schemas.service_config import ServiceConfigSchema, ServiceConfigUpdate
from app.schemas.admin import AdminLogin, AdminToken

__all__ = [
    "FortuneRequest",
    "FortuneResponse",
    "TodayFortuneRequest",
    "SajuFortuneRequest",
    "MatchFortuneRequest",
    "DreamFortuneRequest",
    "SiteConfigSchema",
    "SiteConfigUpdate",
    "ServiceConfigSchema",
    "ServiceConfigUpdate",
    "AdminLogin",
    "AdminToken"
]
