"""
서비스 설정 스키마
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ServiceConfigSchema(BaseModel):
    """서비스 설정 조회"""
    id: int
    code: str
    title: str
    subtitle: str
    description: str
    character_name: str
    character_emoji: str
    is_active: bool
    prompt_template: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ServiceConfigUpdate(BaseModel):
    """서비스 설정 수정"""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    character_name: Optional[str] = None
    character_emoji: Optional[str] = None
    is_active: Optional[bool] = None
    prompt_template: Optional[str] = None
